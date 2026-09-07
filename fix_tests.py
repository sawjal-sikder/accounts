import re

with open('accounts/tests.py', 'r') as f:
    content = f.read()

# Add organization creation to setUp
setup_patch = """    def setUp(self):
        from organization.models.organization import Organization
        self.organization = Organization.objects.create(name="Test Org", email="test@example.com")
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            password="password",
            email="admin@example.com",
            organization=self.organization
        )"""
content = re.sub(r'    def setUp\(self\):\n        User = get_user_model\(\)\n        self.user = User.objects.create_superuser\(\n            username="admin",\n            password="password",\n            email="admin@example.com"\n        \)', setup_patch, content)

# Add organization=self.organization to Group and Account creation in setUp
content = re.sub(r'(AccountGroup\.objects\.create\()', r'\1organization=self.organization, ', content)
content = re.sub(r'(Account\.objects\.create\()', r'\1organization=self.organization, ', content)
content = re.sub(r'(Journal\.objects\.create\()', r'\1organization=self.organization, ', content)

with open('accounts/tests.py', 'w') as f:
    f.write(content)
