from app.modules.users.user_model import User
from app.modules.users.user_repository import UserRepository
from app.modules.users.user_schema import MeResponse, UpdateProfileResponse, UploadAvatarResponse
from app.core.supabase_storage import (
    generate_signed_url,
    is_storage_path,
    upload_profile_image,
)


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _resolve_profile_url(self, profile_url: str | None) -> str | None:
        """
        If profile_url is a Supabase storage path → generate signed URL.
        If it's an external URL (Google) → return as-is.
        If None → return None.
        """
        if profile_url is None:
            return None
        if is_storage_path(profile_url):
            return generate_signed_url(profile_url)
        return profile_url

    def get_me(self, user_id: str) -> MeResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return MeResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            profile_url=self._resolve_profile_url(user.profile_url),
            bio=user.bio,
        )

    def update_profile(
        self,
        user_id: str,
        username: str | None,
        profile_url: str | None,
        bio: str | None,
    ) -> UpdateProfileResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        updated = self.repo.update_user(
            user,
            username=username,
            profile_url=profile_url,
            bio=bio,
        )

        return UpdateProfileResponse(
            id=updated.id,
            email=updated.email,
            username=updated.username,
            profile_url=self._resolve_profile_url(updated.profile_url),
            bio=updated.bio,
        )

    def upload_avatar(
        self,
        user_id: str,
        file_bytes: bytes,
        content_type: str,
    ) -> UploadAvatarResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Upload to Supabase Storage (upsert — overwrites old file)
        path = upload_profile_image(user_id, file_bytes, content_type)

        # Save storage path (not URL) in DB
        self.repo.update_user(user, profile_url=path)

        return UploadAvatarResponse(path=path)