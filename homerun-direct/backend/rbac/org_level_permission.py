from django.core.exceptions import PermissionDenied



def apply_organization_level_filter(request, must_clauses: list):
    """
    Adds organization-level access filtering to the provided must_clauses list.
    
    This checks if the user is not a superuser and applies organization access limits
    using IDs from session['organization_ids'].
    """
    user = request.user
    if not user.is_superuser:
        user_org_ids = request.session.get("organization_ids", [])
        if user_org_ids:
            must_clauses.append({
                "terms": {
                    "id": list(user_org_ids)
                }
            })
        else:
            print("⚠️ No organization_ids found in session.")

def apply_brand_level_filter(request, must_clauses: list):
    """
    Appends brand-level permission filter for non-superusers using session data.
    """
    user = request.user
    if not user.is_superuser:
        print("Noooooooooooooooooooooooooot Suuuuuuuuuuuuuuuuuuuuuuuper")
        brand_ids = request.session.get("brand_ids", [])
        if not brand_ids:
            raise PermissionDenied("No brand access defined for this user.")
        must_clauses.append({
            "terms": {
                "id": list(brand_ids)
            }
        })