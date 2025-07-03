from rest_framework.permissions import BasePermission
from rbac.models import AuthEntityPermission

class EntityPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        entity_name = getattr(view, "basename", "").lower()

        # Force correct entity name if missing
        if not entity_name:
            entity_name = "user"

        org_group = user.group

        print("\n🚀 DEBUG: Checking permissions...")
        print(f"User: {user.username}")
        print(f"Organization: {user.organization}")
        print(f"Group: {org_group}")
        print(f"Entity being accessed: {entity_name}")  # ✅ Now should print "user"
        print(f"Request method: {request.method}")

        if not user.is_authenticated:
            print("❌ User is not authenticated")
            return False

        if not user.organization or not org_group:
            print("❌ User has no organization or group")
            return False

        # Super Admins have full access
        if org_group.is_super_admin:
            print("✅ User is a Super Admin, granting access")
            return True

        # Fetch permission for this entity
        permission = AuthEntityPermission.objects.filter(
            organization=user.organization,
            group=org_group,
            entity_name=entity_name  # ✅ Now should match "user"
        ).first()

        print(f"🔍 Found Permission: {permission}")

        if not permission:
            print("❌ No permission record found")
            return False

        # Check CRUD permissions
        if request.method == "POST" and not permission.can_create:
            print("❌ User does not have CREATE permission")
            return False
        if request.method == "GET" and not permission.can_read:
            print("❌ User does not have READ permission")
            return False
        if request.method in ["PUT", "PATCH"] and not permission.can_update:
            print("❌ User does not have UPDATE permission")
            return False
        if request.method == "DELETE" and not permission.can_delete:
            print("❌ User does not have DELETE permission")
            return False

        print("✅ User has permission, granting access")
        return True
