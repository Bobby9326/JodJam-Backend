import httpx

from app.core.config import settings

SUPABASE_URL = settings.SUPABASE_URL
SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
BUCKET = "entries"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "apikey": SERVICE_ROLE_KEY,
    }


def upload_profile_image(user_id: str, file_bytes: bytes, content_type: str) -> str:
    """
    Upload (upsert) profile image to entries/profile/{user_id}.
    Returns the storage path (not a URL).
    """
    path = f"profile/{user_id}"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"

    headers = _headers()
    headers["Content-Type"] = content_type
    headers["x-upsert"] = "true"  # overwrite existing

    with httpx.Client() as client:
        response = client.post(url, content=file_bytes, headers=headers)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed: {response.status_code} — {response.text}")

    return path  # e.g. "profile/abc123"


def generate_signed_url(path: str, expires_in: int = 3600) -> str:
    """
    Generate a signed URL for a private storage object.
    `path` is relative to the bucket, e.g. "profile/abc123".
    """
    url = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET}/{path}"

    with httpx.Client() as client:
        response = client.post(
            url,
            json={"expiresIn": expires_in},
            headers=_headers(),
        )

    if response.status_code != 200:
        raise RuntimeError(f"Signed URL failed: {response.status_code} — {response.text}")

    signed_url = response.json().get("signedURL")
    if not signed_url:
        raise RuntimeError("No signedURL in response")

    # signedURL from Supabase is a relative path like /object/sign/...
    # Need to prepend SUPABASE_URL + /storage/v1
    if signed_url.startswith("/object/sign/"):
        return f"{SUPABASE_URL}/storage/v1{signed_url}"

    # Already absolute
    if signed_url.startswith("http"):
        return signed_url

    # Fallback
    return f"{SUPABASE_URL}{signed_url}" 


def is_storage_path(profile_url: str | None) -> bool:
    """
    Returns True if profile_url is a storage path (not an external URL).
    Storage paths look like "profile/abc123" (no http scheme).
    """
    if not profile_url:
        return False
    return not profile_url.startswith("http://") and not profile_url.startswith("https://")


def upload_memory_image(user_id: str, date_str: str, file_bytes: bytes, content_type: str) -> str:
    """
    Upload memory image to entries/memories/{user_id}/{date}.
    No upsert — memory is immutable, upload once only.
    Returns the storage path.
    """
    path = f"memories/{user_id}/{date_str}"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{path}"

    headers = _headers()
    headers["Content-Type"] = content_type
    # x-upsert intentionally omitted — memories cannot be overwritten

    with httpx.Client() as client:
        response = client.post(url, content=file_bytes, headers=headers)

    if response.status_code not in (200, 201):
        raise RuntimeError(f"Upload failed: {response.status_code} — {response.text}")

    return path  # e.g. "memories/abc123/2026-05-26"