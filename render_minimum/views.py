"""
View functions for the public post application.

Handles:
- Public post listing and detail views.
- Post submission with validation.
- Confirmation page and endpoint.
- Moderation review pages and endpoints.
- Account authentication (login/logout).
- Health check endpoint.
"""

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.http import HttpRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from datetime import timezone
from urllib.parse import unquote, parse_qs, urlparse
from render_minimum.forms import SubmissionForm


def classification_result(text: str) -> str:
    """Classify post - placeholder implementation."""
    if settings.AI_CLASSIFIER_RESULT_DOUBTFUL_FIRST:
        return "DOUBTFUL"
    return "SAFE"


def public_post_list(request: HttpRequest) -> HttpResponseNotAllowed:
    """
    Display a paginated list of PUBLIC posts.

    Shows newest posts first with:
    - Username
    - Post text (escaped)
    - Publication date
    """
    # Only show PUBLIC state posts.
    public_posts = Post.objects.filter(state=Post.PUBLIC).order_by("-created_at")

    # Paginate.
    page_number = request.GET.get("page", 1)
    paginator = Paginator(public_posts, 20)  # 20 posts per page.
    try:
        posts_page = paginator.page(page_number)
    except Exception as exc:
        raise exc

    return render(
        request,
        "posts/list.html",
        {
            "posts": posts_page.object_list,
            "page_number": int(page_number),
            "paginator": paginator,
        },
    )


def public_post_detail(request: HttpRequest, pk: int) -> HttpResponseNotAllowed:
    """Display a single PUBLIC post."""
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    # Only show PUBLIC state posts.
    if post.state != Post.PUBLIC:
        return render(request, "posts/not_public.html", {"post": post})

    return render(request, "posts/detail.html", {"post": post})


def normalize_email(email: str) -> str:
    """
    Normalize email addresses for consistent storage.

    Rules:
    - Convert to lowercase.
    - Strip leading/trailing whitespace.
    - Remove quotes around the address if present.

    Note: We do not remove dots or plus-addresses as this can break replies.
    """
    import re

    email = email.strip().lower()

    # Remove surrounding quotes if present.
    if (email.startswith('"') and email.endswith('"')) or \
       (email.startswith("'") and email.endswith("'")):
        email = email[1:-1]

    return email


def submit_post(request: HttpRequest) -> HttpResponseNotAllowed:
    """
    Handle post submission form.

    Fields:
    - email: Email address for confirmation.
    - username: Display name.
    - text: Post content.

    Validation:
    - Server-side validation of all fields.
    - Temporary email block (cooldown).
    - Preserve input on recoverable errors.

    Returns the form with errors if validation fails.
    """

    # Create form instance with user-supplied data.
    initial_data = {}
    if request.method == "POST":
        initial_data["email"] = request.POST.get("email", "")
        initial_data["username"] = request.POST.get("username", "")
        initial_data["text"] = request.POST.get("text", "")

        # Re-use the same input for error display.
    elif request.method == "GET":
        if request.GET:
            qs_params = request.META.get("QUERY_STRING", "")
            for key in ["email", "username", "text"]:
                if key in qs_params and qs_params[key]:
                    initial_data[key] = urllib.parse.unquote(qs_params[qs_params.find(key):].split("&")[0])

    form = SubmissionForm(initial=initial_data)

    if request.method == "POST":
        # Form was submitted, validate.
        if not form.is_valid():
            return render(request, "submit.html", {"form": form})

        email = normalize_email(form.cleaned_data["email"])
        username = form.cleaned_data["username"]
        text = form.cleaned_data["text"]

        # Check cooldown - this is a shared database check to prevent race conditions.
        with db_transaction.atomic():
            cooldown_record = CooldownRecord.check_and_create_if_needed(email)

            if cooldown_record and not cooldown_record.is_expired:
                # Still within cooldown window.
                now = timezone.now()
                age_seconds = cooldown_record.expires_at - now.timestamp()
                hours_left = max(0, (cooldown_record.expires_at - now.timestamp()) / 3600)

                return render(
                    request,
                    "submit.html",
                    {
                        "form": form,
                        "is_cooldown": True,
                        "cooldown_hours_left": f"{hours_left:.1f}",
                    },
                )

    # Form passed validation (or was GET), proceed to create post.
    return render(request, "submit.html", {"form": form})


def confirmation_page(
    request: HttpRequest,
    pk: int,
    token: str,
) -> HttpResponseNotAllowed:
    """
    Display the confirmation page for a post awaiting confirmation.

    Shows:
    - Username and full post text.
    - Remaining confirmation time (from server time).
    - Confirm button.

    GET requests do not change state. Only POST confirms the post.
    """

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    if post.state != Post.AWAITING_CONFIRMATION:
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    try:
        # Verify the token exists and is valid.
        token_hash = tokenize(token)
        token_obj = ConfirmationToken.objects.get(
            post=post,
            token_hash=token_hash,
        )
    except ConfirmationToken.DoesNotExist:
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    if token_obj.consumed:
        # Token already consumed.
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    # Calculate remaining time from server.
    age_seconds = post.created_at - timezone.now().timestamp()
    remaining_seconds = max(0, settings.CONFIRMATION_DEADLINE_SECONDS - age_seconds)

    return render(request, "confirmation.html", {
        "post": post,
        "username": escape(post.username),
        "text": escape(post.text[:500]),  # Show first 500 chars.
        "remaining_seconds": int(remaining_seconds),
        "token_valid": True,
    })


def confirm_post(
    request: HttpRequest,
    pk: int,
    token: str,
) -> HttpResponseNotAllowed:
    """
    Process confirmation of a post.

    Requires CSRF protection via POST request.
    Validates token and confirms the post atomically.
    Creates an AI task after confirmation.
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # Check CSRF token.
    if not request.session.get("csrf_token"):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            from django.http import Http404
            raise Http404("Post not found")
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    # Only AWAITING_CONFIRMATION can be confirmed.
    if post.state != Post.AWAITING_CONFIRMATION:
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    try:
        token_hash = tokenize(token)
        token_obj = ConfirmationToken.objects.get(
            post=post,
            token_hash=token_hash,
        )
    except ConfirmationToken.DoesNotExist:
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    if token_obj.consumed or token_obj.is_expired:
        return render(request, "confirmation.html", {
            "post": post,
            "show_confirm": False,
        })

    # Confirm the post atomically.
    with db_transaction.atomic():
        success = post.consume_confirmation_token(token)
        if not success:
            return render(request, "confirmation.html", {
                "post": post,
                "show_confirm": False,
            })

        # Create an AI task.
        ai_result = classification_result(post.text)  # Always DOUBTFUL in initial implementation.

        # Update post state based on AI result.
        if ai_result == "SAFE":
            post.state = Post.PUBLIC
            post.published_at = timezone.now().timestamp()
            email_task = EmailTaskQueue.objects.create(
                post=post,
                recipient_email=post.author_email,
                subject="Your post has been published",
                body=(
                    f"Your post from {post.username} has been reviewed and is now PUBLIC."
                ),
            )
        elif ai_result == "UNSAFE":
            post.state = Post.REJECTED
            email_task = EmailTaskQueue.objects.create(
                post=post,
                recipient_email=post.author_email,
                subject="Your post has been rejected",
                body=(
                    f"Your post from {post.username} has been reviewed and does not meet our guidelines. "
                    "It will be removed shortly."
                ),
            )
        else:  # DOUBTFUL
            post.state = Post.AWAITING_MODERATION
            moderator_token = ModeratorToken.create_for_post(post)
            email_task = EmailTaskQueue.objects.create(
                post=post,
                recipient_email=settings.MODERATOR_EMAIL,
                subject=f"Review required: {post.username}",
                body=(
                    f"A new post requires your review.\n\n"
                    f"Post ID: {post.pk}\n"
                    f"Username: {post.username}"
                ),
            )

        # Clean up old tokens for this post.
        ConfirmationToken.objects.filter(post=post).exclude(pk=token_obj.pk).delete()
        ModeratorToken.objects.filter(post=post).delete()

    return redirect(settings.PUBLIC_BASE_URL + "/")


def moderation_page(
    request: HttpRequest,
    pk: int,
    token: str,
) -> HttpResponseNotAllowed:
    """Display the moderation review page."""

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    if post.state != Post.AWAITING_MODERATION:
        return render(request, "moderation.html", {
            "post": post,
            "show_buttons": False,
        })

    try:
        token_hash = tokenize(token)
        token_obj = ModeratorToken.objects.get(
            post=post,
            token_hash=token_hash,
        )
    except ModeratorToken.DoesNotExist:
        return render(request, "moderation.html", {
            "post": post,
            "show_buttons": False,
        })

    if token_obj.is_expired:
        return render(request, "moderation.html", {
            "post": post,
            "show_buttons": False,
        })

    review_url = urllib.parse.quote(settings.PUBLIC_BASE_URL + f"/review/{pk}/{token_obj.token_hash}/")
    accept_url = urllib.parse.quote(settings.PUBLIC_BASE_URL + f"/review/{pk}/{token_obj.token_hash}/accept/")
    reject_url = urllib.parse.quote(settings.PUBLIC_BASE_URL + f"/review/{pk}/{token_obj.token_hash}/reject/")

    return render(request, "moderation.html", {
        "post": post,
        "username": escape(post.username),
        "author_email": post.author_email,
        "post_text": escape(post.text[:500]),
        "submission_time": timezone.localtime(post.created_at).strftime("%Y-%m-%d %H:%M:%S"),
        "current_state": post.state_name,
        "review_url": review_url,
        "accept_url": accept_url,
        "reject_url": reject_url,
    })


def accept_moderation(
    request: HttpRequest,
    pk: int,
    token: str,
) -> HttpResponseNotAllowed:
    """Accept the moderation decision - make post PUBLIC."""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    if post.state != Post.AWAITING_MODERATION:
        from django.http import Http404
        raise Http404("Invalid post state")

    try:
        token_hash = tokenize(token)
        token_obj = ModeratorToken.objects.get(
            post=post,
            token_hash=token_hash,
        )
    except ModeratorToken.DoesNotExist:
        return redirect(settings.PUBLIC_BASE_URL + "/post/")

    if token_obj.is_expired:
        return redirect(settings.PUBLIC_BASE_URL + "/post/")

    now = timezone.now()

    with db_transaction.atomic():
        post.state = Post.PUBLIC
        post.published_at = now.timestamp()
        post.save(update_fields=["state", "published_at"])

        # Consume and remove moderator token.
        ModeratorToken.objects.filter(
            pk=token_obj.pk,
            post=post,
        ).delete()

    return redirect(settings.PUBLIC_BASE_URL + "/post/")


def reject_moderation(
    request: HttpRequest,
    pk: int,
    token: str,
) -> HttpResponseNotAllowed:
    """Reject the moderation decision - make post REJECTED."""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    if post.state != Post.AWAITING_MODERATION:
        from django.http import Http404
        raise Http404("Invalid post state")

    try:
        token_hash = tokenize(token)
        token_obj = ModeratorToken.objects.get(
            post=post,
            token_hash=token_hash,
        )
    except ModeratorToken.DoesNotExist:
        return redirect(settings.PUBLIC_BASE_URL + "/post/")

    if token_obj.is_expired:
        return redirect(settings.PUBLIC_BASE_URL + "/post/")

    from .models import EmailTaskQueue as EmailTaskQueueModel

    with db_transaction.atomic():
        post.state = Post.REJECTED
        post.save(update_fields=["state"])

        # Send rejection email to author.
        email_task = EmailTaskQueueModel.objects.create(
            post=post,
            recipient_email=post.author_email,
            subject="Your post has been rejected",
            body=(
                f"Your post from {post.username} has been reviewed and does not meet our guidelines. "
                "It will be removed shortly."
            ),
        )

        # Consume moderator token.
        ModeratorToken.objects.filter(
            pk=token_obj.pk,
            post=post,
        ).delete()

    return redirect(settings.PUBLIC_BASE_URL + "/post/")


def health_check(request: HttpRequest) -> JsonResponse:
    """Health check endpoint for monitoring and load balancers."""

    from django.db import connection
    db_settings = connection.settings_dict

    # Return basic health status.
    return JsonResponse({
        "status": "healthy",
        "django_version": __import__("django").get_version(),
        "database_engine": db_settings.get("ENGINE", "unknown"),
    })


def logout_view(request: HttpRequest) -> HttpResponseNotAllowed:
    """Logout view using Django's built-in functionality."""

    if request.method == "POST":
        logout(request)
    return redirect(settings.PUBLIC_BASE_URL + "/")


def tokenize(data: str, salt: str = "salt") -> str:
    """Tokenize data for storage - simple salted hash approach."""

    import hashlib
    # Combine data with a unique identifier and hash it.
    return hashlib.sha256((f"{salt}:{data}").encode()).hexdigest()
