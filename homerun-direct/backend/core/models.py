from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps


# Base model with automatic timestamps and extra fields
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Ensures this model is only used as a base class


class Entity(models.Model):
    name = models.CharField(max_length=100)
    url_path = models.CharField(max_length=255, unique=True)
    model_path = models.CharField(max_length=255, help_text="e.g. rbac.Organizations")

    meta = models.JSONField(default=dict, blank=True)
    form = models.JSONField(default=dict, blank=True)
    actions = models.JSONField(default=dict, blank=True)
    table = models.JSONField(default=dict, blank=True)
    layout = models.JSONField(default=list, blank=True)
    permissions = models.JSONField(default=list, blank=True)
    POST = models.JSONField(default=dict, blank=True)
    # ✅ New fields for dynamic UI schema
    # {"type": "heading_dynamic", "headingType": "h2", "label": "Let's Get Started", "tab": "setup_organizations"}
    post_heading = models.JSONField(default=dict, blank=True)
    # {"type": "description", "description": "Setting up your Organization will be quick and easy. Start by telling us a few basics about your Organization.", "tab": "setup_organizations"}
    post_description = models.JSONField(default=dict, blank=True)
    extra_field = models.JSONField(default=dict, blank=True)
    extra_parameter = models.JSONField(default=dict, blank=True)
    # {"setup_organizations": ["organization_name"]}
    post_tabs = models.JSONField(default=dict, blank=True)

    post_order = models.JSONField(null=True, blank=True)  # <== New field

    def __str__(self):
        return f"{self.name} - {self.url_path}"

    def get_model_class(self):
        try:
            app_label, model_name = self.model_path.split(".")
            return apps.get_model(app_label, model_name)
        except Exception as e:
            raise ImproperlyConfigured(
                f"Invalid model_path: {self.model_path}. Error: {e}"
            )

    def build_post_schema(self):
        model_class = self.get_model_class()
        fields = {}

        # ✅ Inject heading and description if defined
        if self.post_heading:
            fields["heading"] = self.post_heading

        if self.post_description:
            fields["description"] = self.post_description

        # if self.extra_field:
        #     fields["extra_field"] = self.extra_field

        # if self.extra_parameter:
        #     fields["extra_parameter"] = self.extra_parameter

        for field in model_class._meta.get_fields():
            if field.auto_created or not hasattr(field, "verbose_name"):
                continue

            if isinstance(field, models.ForeignKey):
                rel_model = field.related_model
                options = []

                for obj in rel_model.objects.all():
                    option = {"id": obj.pk}
                    if hasattr(obj, "label"):
                        option["label"] = obj.label
                    if hasattr(obj, "value"):
                        option["value"] = obj.value
                    if "label" not in option:
                        option["label"] = str(obj)
                    if "value" not in option:
                        option["value"] = str(obj)
                    options.append(option)

                fields[field.name] = {
                    "type": "select",
                    "label": field.verbose_name.title(),
                    "bindLabel": "label",
                    "bindValue": "id",
                    "options": options,
                    "required": not field.blank,
                }

            elif isinstance(field, (models.CharField, models.TextField)):
                fields[field.name] = {
                    "type": "string",
                    "label": field.verbose_name.title(),
                    "max_length": field.max_length or 255,
                    "required": not field.blank,
                }

            elif isinstance(field, models.BooleanField):
                fields[field.name] = {
                    "type": "checkbox",
                    "label": field.verbose_name.title(),
                    "required": False,
                }

            elif isinstance(field, models.IntegerField):
                fields[field.name] = {
                    "type": "number",
                    "label": field.verbose_name.title(),
                    "required": not field.blank,
                }

            elif isinstance(field, models.DateField):
                fields[field.name] = {
                    "type": "date",
                    "label": field.verbose_name.title(),
                    "required": not field.blank,
                }

        return fields

    def save(self, *args, **kwargs):
        self.meta.setdefault("title", self.name)
        self.meta.setdefault("description", "")

        self.form.setdefault("title", f"{self.name} Form")
        self.form["entity"] = self.url_path

        if not self.layout:
            self.layout = [
                {
                    "template": "default-style",
                    "url": self.url_path.replace("/api", ""),
                    "entity": self.url_path,
                    "api": [],
                }
            ]
        if not self.POST:
            self.POST = self.build_post_schema()

        super().save(*args, **kwargs)

    def get_options_response(self, absolute_url):
        layout_with_entity = [
            {**block, "entity": absolute_url} for block in self.layout
        ]
        return {
            "meta": self.meta,
            "form": {**self.form, "entity": absolute_url},
            "actions": self.actions,
            "table": self.table,
            "layout": layout_with_entity,
            "permissions": self.permissions,
            "POST": self.POST,
        }
