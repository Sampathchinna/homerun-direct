from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel,Entity
from organization.models import Organization
from core.models import Entity
from property.models import *
#>> Statement  Pyment Invoice [Entities] Propert List []



class  DirectUser(AbstractUser,BaseModel):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)  # Ensure email uniqueness
    encrypted_password=models.CharField(max_length=64,null=True, blank=True) # MAX(LENGTH(encrypted_password)) => 60
    telephone=models.CharField(max_length=30,null=True, blank=True) # MAX(LENGTH(telephone)) FROM ant.users => 29
    
    name = models.CharField(max_length=255,null=True, blank=True)
    # remove first_name and last_name
    first_name = None
    last_name = None
    rvshare_user_id = models.CharField(max_length=10, blank=True, null=True)
    stripe_plan_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class OrganizationProperty(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)


class OrganizatioRole(BaseModel):

    """<T>OrganizatioRole
    1     Employee
    2     TeamMember
    3     Customer

    Different organizations they can have different roles

SELECT * FROM ant.users; # Who is logging # Organization has user_id  means he is admin .

# Organization can have empoloyee
# Employee is nothing but a user.
# Organization can ereate employee [NOthing but a user]
# OrganizationHeirarchy one  value is Employee => initate_master_data

>> <T>UserRoles :: Admin ne employee ko add kiya
    OrganizatioRole <==> user_id   <==> organization_id
       'Employee'      nishant
       Teamnmenr

<t>Pemrmissions
   Entity  | OrganizatioRole | create | read | update | delete | custom_json


>> unit level , >> proprty level


SELECT * FROM ant.employees;
-- SELECT * FROM ant.employee_access_roles;
-- SELECT * FROM ant.employee_permissions;
SELECT * FROM ant.teams;
SELECT * FROM ant.team_members;
SELECT distinct(member_
type) FROM ant.team_members; -- Only Employee
-- SELECT * FROM ant.employee_portfolios; -- Empty
-- SELECT * FROM ant.employees_properties;
--
SELECT DISTINCT(all_id) FROM ant.employees_properties -- Only 0
-- SELECT * FROM ant.employees_units;
--
SELECT DISTINCT(all_id) FROM ant.employees_units -- Only 0
⇒ brand, unit, unit listings , property Fetch YOur Vrbo ticket
SELECT * FROM ant.customers;
SELECT * FROM ant.channel_users;;
SELECT distinct(direct_user_type) FROM ant.channel_users;
SELECT * FROM ant.brands_employees; -- Must be join to employees
SELECT * FROM ant.guests; -- No Password obviously
SELECT * FROM ant.partner_access_organizations;
SELECT * FROM ant.partner_accesses; -- What is access key

          """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="groups", null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.organization.organization_name if self.organization else 'None'} - {self.name}"



class AuthEntityPermission(BaseModel):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="entity_permissions", null=True, blank=True
    )
    group = models.ForeignKey(OrganizatioRole, on_delete=models.CASCADE, related_name="permissions")
    entity_name = models.ForeignKey(Entity, on_delete=models.CASCADE)  # Ensure this is correct
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    custom_permissions = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        unique_together = ("organization", "group", "entity_name")


    def __str__(self):
        org_name = self.organization.organization_name if self.organization else "None"
        entity_name = getattr(self.entity_name, "name", "Unknown Entity")  # Avoid attribute error
        return f"{org_name} - {self.group.name} - {entity_name}"
