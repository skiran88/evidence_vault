from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.category_name

class Custom_user(models.Model):
    user_id=models.OneToOneField(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    address=models.CharField(max_length=500)
    phone=models.CharField(max_length=15)
    email=models.CharField(max_length=225)
    gender=models.CharField(max_length=15)


class Advocate(models.Model):
    user_id=models.OneToOneField(User,on_delete=models.CASCADE)
    CATEGORY=models.ForeignKey(Category,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=225)
    experience=models.CharField(max_length=50)
    proof=models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, default="Pending")


class CaseRequest(models.Model):
    case_title = models.CharField(max_length=200)


    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    description = models.TextField(default="No description")

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, null=True, blank=True)

    evidence_file = models.FileField(upload_to='evidence/', null=True, blank=True)

    court_location = models.CharField(max_length=200)
    court = models.ForeignKey('Court', on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
            ("Case Assigned To Court", "Case Assigned To Court"),
            ("Court Accepted", "Court Accepted"),
            ("Court Rejected", "Court Rejected"),
            ("Under Trial", "Under Trial"),
            ("Awaiting Verdict", "Awaiting Verdict"),
            ("Case Disposed", "Case Disposed")
        ],
        default="Pending"
    )

    def __str__(self):
        return self.case_title

    advocate_response = models.TextField(null=True, blank=True)
    evidence_hash = models.CharField(max_length=64, null=True, blank=True)
    blockchain_txn_hash = models.CharField(max_length=66, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Case_details(models.Model):
    request_id = models.ForeignKey(CaseRequest, on_delete=models.CASCADE)
    date_uploaded=models.DateField()


class court_hearing(models.Model):
    case_id = models.ForeignKey(Case_details, on_delete=models.CASCADE)
    hearing_date=models.DateField()
    verdict=models.CharField(max_length=500)
    notes=models.CharField(max_length=150)





class CaseDetails(models.Model):
    case = models.ForeignKey(CaseRequest, on_delete=models.CASCADE)
    date_uploaded = models.DateField()


class CourtHearing(models.Model):
    case = models.ForeignKey(CaseRequest, on_delete=models.CASCADE)
    hearing_date = models.DateField()
    verdict = models.CharField(max_length=500)
    notes = models.CharField(max_length=150)



class Court(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    court_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    court_type = models.CharField(max_length=50, null=True, blank=True)
    email=models.EmailField(max_length=225)


class Evidence(models.Model):
    case = models.ForeignKey(CaseRequest, on_delete=models.CASCADE, related_name='evidence_uploads')
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE)
    evidence_file = models.FileField(upload_to='evidence/advocate/')
    description = models.TextField()
    evidence_hash = models.CharField(max_length=64, null=True, blank=True)
    blockchain_txn_hash = models.CharField(max_length=66, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for CASE #{self.case.id}"


class CourtCase(models.Model):
    case_title = models.CharField(max_length=200)
    description = models.TextField()

    court = models.ForeignKey('Court', on_delete=models.CASCADE)
    advocate = models.ForeignKey('Advocate', on_delete=models.CASCADE)

    case_file = models.FileField(upload_to='court_cases/', null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=[
            ("Assigned", "Assigned"),
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
            ("Under Trial", "Under Trial"),
            ("Closed", "Closed")
        ],
        default="Assigned"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Court Case #{self.id} - {self.case_title}"