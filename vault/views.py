
import smtplib

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .models import *
from .blockchain_utils import blockchain_helper as bh


def home(request):
    return render(request, 'index.html')
# USER REGISTER
def user_register(request):

    if request.method == 'POST':

        fullname = request.POST['fullname']
        phone = request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']

        username = email   # using email as username

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect('user_register')

        # create django user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # split fullname
        name = fullname.split(" ")

        first_name = name[0]
        last_name = name[1] if len(name) > 1 else ""

        # create custom user
        Custom_user.objects.create(
            user_id=user,
            first_name=first_name,
            last_name=last_name,
            address="",
            phone=phone,
            email=email,
            gender=""
        )

        messages.success(request, "Registration Successful")
        return redirect('login')

    return render(request, 'user_register.html')

def login(request):

    if request.method == "POST":

        identifier = request.POST['identifier']
        password = request.POST['password']

        user = authenticate(request, username=identifier, password=password)


        if user is not None:

            if Custom_user.objects.filter(user_id=user).exists():
                auth_login(request, user)
                return redirect('user_dashboard')

            elif Advocate.objects.filter(user_id=user).exists():

                advocate = Advocate.objects.get(user_id=user)

                if advocate.status == "Approved":
                    auth_login(request, user)
                    return redirect('advocate_dashboard')

                elif advocate.status == "Pending":
                    messages.error(request, "Your account is waiting for admin approval")
                    return redirect('login')

                elif advocate.status == "Rejected":
                    messages.error(request, "Your registration was rejected by admin")
                    return redirect('login')
                    # 🆕 COURT LOGIN

            elif Court.objects.filter(user_id=user).exists():
                court = Court.objects.get(user_id=user)
                user = authenticate(request, username=identifier, password=password)
                auth_login(request, user)
                # optional session
                request.session['court_name'] = court.court_name
                return redirect('court_dashboard')



            elif user.is_superuser:
                auth_login(request, user)
                return redirect("admin_dashboard")

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


def advocate_register(request):

    if request.method == "POST":

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        email = request.POST['email']
        experience = request.POST['experience']
        username = request.POST['email']
        password = request.POST['password']
        proof = request.FILES['proof']


        category_id = request.POST.get('category_name')
        category = Category.objects.get(id=category_id)

        # create login account
        user = User.objects.create_user(
            username=username,
            password=password,

        )

        # create advocate profile
        Advocate.objects.create(
            user_id=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            experience=experience,
            proof=proof,
            CATEGORY=category,  # ✅ correct
            status="Pending"
        )

        return redirect("login")

    # ✅ THIS IS MISSING (for dropdown to work)
    categories = Category.objects.all()

    return render(request, "advocate_register.html", {
        'categories': categories
    })

@login_required(login_url='login')
def admin_dashboard(request):
    current_block = bh.get_current_block() if bh else 0
    return render(request, 'admin_dashboard.html', {'current_block': current_block})
def add_categories(request):
    if request.method == "POST":
        name = request.POST.get('category_name')
        desc = request.POST.get('description')

        Category.objects.create(
            category_name=name,
            description=desc
        )

        return redirect('add_categories')  # after saving

    # 🔴 THIS WAS MISSING (for GET request)
    categories = Category.objects.all()
    return render(request, 'add_categories.html', {'categories': categories})
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('add_categories')
def approve_advocates(request, adv_id=None, action=None):

    # handle approve / reject action
    if adv_id and action:
        adv = Advocate.objects.get(id=adv_id)

        if action == "approve":
            adv.status = "Approved"
        elif action == "reject":
            adv.status = "Rejected"

        adv.save()
        return redirect("approve_advocates")

    # load page
    advocates = Advocate.objects.all()

    return render(request, "approve_advocates.html", {
        "advocates": advocates
    })


def blockchain_transactions(request):
    # Fetch all cases for monitoring
    cases = CaseRequest.objects.all().order_by('-created_at')
    current_block = bh.get_current_block() if bh else 0
    return render(request, 'blockchain_transactions.html', {
        'cases': cases,
        'current_block': current_block
    })
def view_users_accounts(request):

    users = Custom_user.objects.all()

    return render(request,"view_users_accounts.html",{
        "users":users
    })
def delete_user(request,id):

    user = Custom_user.objects.get(id=id)

    user.user_id.delete()
    user.delete()
    return redirect('view_users_accounts')
def view_complaints(request):
    return render(request,'view_complaints.html')
def user_dashboard(request):
    return render(request,'user_dashboard.html')
def advocate_dashboard(request):
    return render(request,'advocate_dashboard.html')
def upload_evidence(request):
    return render(request,'upload_evidence.html')

from .models import CaseRequest, Advocate

@login_required
def submit_case_request(request):

    advocates = Advocate.objects.all()
    categories = Category.objects.all()
    print(categories)  # 👈 add this



    if request.method == "POST":
        case = CaseRequest.objects.create(
            case_title=request.POST.get("case_title"),
            category_id=request.POST.get("category"),  
            description=request.POST.get("description"),
            evidence_file=request.FILES.get("evidence_file"),
            advocate_id=request.POST.get("advocate_id"),
            court_location=request.POST.get("court_location"),
            user=request.user
        )

        # ⛓️ Blockchain Integration
        if case.evidence_file and bh:
            try:
                # Read file content for hashing
                file_content = case.evidence_file.read()
                evidence_hash, tx_hash = bh.store_evidence(file_content, case.id)
                
                # Update case with blockchain details
                case.evidence_hash = evidence_hash
                case.blockchain_txn_hash = tx_hash
                case.save()
                
                messages.success(request, f"Evidence secured on blockchain. Txn: {tx_hash[:10]}...")
            except Exception as e:
                print(f"Blockchain Error: {e}")
        case.save()

        # Update CaseRequest if needed or redirect
        return redirect('submit_case_request')

    return render(request, 'submit_case_request.html', {
        'advocates': advocates,
        'categories': categories
    })
def view_categories(request):
    categories = Category.objects.all()
    advocates = Advocate.objects.filter(status="Approved")

    # 🔍 Search by name
    query = request.GET.get('q')
    if query:
        advocates = advocates.filter(
            models.Q(first_name__icontains=query) | 
            models.Q(last_name__icontains=query)
        )

    # 📁 Filter by category
    category_id = request.GET.get('category')
    if category_id:
        advocates = advocates.filter(CATEGORY_id=category_id)

    return render(request, 'view_categories.html', {
        'categories': categories,
        'advocates': advocates,
        'query': query,
        'selected_category': int(category_id) if category_id else None,
        "show_back_button": True
    })
def user_dashboard(request):
    return render(request, "user_dashboard.html", {
        "show_back_button": False
    })

def case_action(request, case_id, action):
    case = CaseRequest.objects.get(id=case_id)

    if action == "approve":
        case.status = "Approved"
        case.advocate_response = "Your case has been accepted by the advocate."

    elif action == "reject":
        case.status = "Rejected"
        case.advocate_response = "Your case has been rejected by the advocate."

    case.save()

    return redirect('view_case_requests')

def view_advocate_responses(request):
    cases = CaseRequest.objects.filter(user=request.user).exclude(advocate_response=None)
    return render(request, 'view_advocate_responses.html', {'cases': cases})
def view_case_requests(request):
    advocate = Advocate.objects.get(user_id=request.user)
    cases = CaseRequest.objects.filter(advocate=advocate)
    return render(request, 'view_case_requests.html', {'cases': cases})



def manage_court(request):

    if request.method == "POST":
        print("FORM SUBMITTED ✅")

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        court_name = request.POST.get('court_name')
        location = request.POST.get('location')
        court_type = request.POST.get('court_type')

        try:
            # ✅ Check duplicate username
            if User.objects.filter(username=username).exists():
                print("USERNAME EXISTS ❌")
                messages.error(request, "Username already exists")
                return redirect('manage_court')

            # ✅ Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            # ✅ Create court (ONLY ONCE)
            Court.objects.create(
                user_id=user,
                court_name=court_name,
                email=email,
                location=location,
                court_type=court_type
            )

            # 🔥 SEND EMAIL
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login("skiran8445@gmail.com", "xervrzagrvexjodq")

            msg = """Subject: Court Login Details

Hello,

Your court account has been created.

Username: {}
Password: {}

- EvidenceVault
""".format(username, password)

            server.sendmail("skiran8445@gmail.com", email, msg)
            server.quit()

            print("DATA SAVED + EMAIL SENT ✅")
            messages.success(request, "Court added and email sent successfully")

        except Exception as e:
            print("ERROR:", e)
            messages.error(request, "Error: {}".format(e))

        return redirect('manage_court')

    # ✅ THIS MUST BE OUTSIDE POST
    courts = Court.objects.all().order_by('-id')
    return render(request, 'manage_court.html', {'courts': courts})
def delete_court(request, id):

    court = Court.objects.get(id=id)

    # delete linked user also
    court.user_id.delete()

    messages.success(request, "Court deleted successfully")

    return redirect('manage_court')
from .models import Court

def court_dashboard(request):

    # Check login using Django auth
    if not request.user.is_authenticated:
        return redirect('login')

    # Check if this user is a court
    court = Court.objects.filter(user_id=request.user).first()

    if not court:
        return redirect('login')

    return render(request, 'court_dashboard.html', {'court': court})
def responded_cases(request):
    advocate = Advocate.objects.get(user_id=request.user)
    # Include both Approved and Assigned cases
    cases = CaseRequest.objects.filter(
        advocate=advocate, 
        status__in=["Approved", "Case Assigned To Court"]
    ).order_by('-created_at')
    
    courts = Court.objects.all()
    return render(request, 'responded_cases.html', {'cases': cases, 'courts': courts})

def assign_to_court(request, case_id):
    if request.method == "POST":
        court_id = request.POST.get('court_id')
        case = CaseRequest.objects.get(id=case_id)
        court = Court.objects.get(id=court_id)
        
        case.court = court
        case.status = "Case Assigned To Court"
        case.save()
        
        messages.success(request, f"Case Assigned to {court.court_name} successfully")
    return redirect('responded_cases')
@login_required
def upload_documents(request):
    advocate = Advocate.objects.filter(user_id=request.user).first()
    if not advocate:
        messages.error(request, "Access denied. Use advocate credentials.")
        return redirect('login')

    # Fetch cases where advocate is assigned and has a commitment (Accepted or Approved)
    cases = CaseRequest.objects.filter(
        advocate=advocate,
        status__in=["Court Accepted", "Approved", "Under Trial", "Awaiting Verdict"]
    ).order_by('-created_at')

    # Fetch previous evidence uploads for this advocate
    evidence_history = Evidence.objects.filter(advocate=advocate).order_by('-uploaded_at')

    if request.method == "POST":
        case_id = request.POST.get("case_id")
        description = request.POST.get("description")
        evidence_file = request.FILES.get("evidence_file")

        if not case_id or not evidence_file:
            messages.error(request, "Please select a case and provide an evidence file.")
            return redirect('upload_documents')

        case = get_object_or_404(CaseRequest, id=case_id)

        # Create Evidence record
        new_evidence = Evidence.objects.create(
            case=case,
            advocate=advocate,
            evidence_file=evidence_file,
            description=description
        )

        # ⛓️ Blockchain Integration
        if bh:
            try:
                # Use seek(0) to read from start
                new_evidence.evidence_file.seek(0)
                file_content = new_evidence.evidence_file.read()
                evidence_hash, tx_hash = bh.store_evidence(file_content, f"ADV_{case.id}_{new_evidence.id}")
                
                # Save hashes
                new_evidence.evidence_hash = evidence_hash
                new_evidence.blockchain_txn_hash = tx_hash
                new_evidence.save()
                
                messages.success(request, f"Evidence secured on blockchain. Hash: {evidence_hash[:10]}...")
            except Exception as e:
                messages.warning(request, f"Blockchain recording failed: {str(e)}")

        messages.success(request, f"Document uploaded successfully for CASE #{case.id}.")
        return redirect('upload_documents')

    return render(request, 'upload_documents.html', {
        'cases': cases,
        'evidence_history': evidence_history
    })

def view_blockchain_cases(request):
    # Detect user role
    court = Court.objects.filter(user_id=request.user).first()
    advocate = Advocate.objects.filter(user_id=request.user).first()
    
    if not court and not advocate:
        messages.error(request, "Access denied. Please login as a Court or Advocate.")
        return redirect('login')

    if court:
        # Fetch all cases assigned to THIS COURT
        cases = CaseRequest.objects.filter(court=court).order_by('-created_at')
    else:
        # Fetch cases handled by THIS ADVOCATE
        cases = CaseRequest.objects.filter(advocate=advocate).order_by('-created_at')
    
    # Fetch approved advocates for court assignment dropdown
    approved_advocates = Advocate.objects.filter(status="Approved") if court else []
    
    return render(request, 'view_blockchain_cases.html', {
        'cases': cases,
        'advocates': approved_advocates,
        'is_court': court is not None
    })


def court_assign_advocate(request, case_id):
    if request.method == "POST":
        advocate_id = request.POST.get('advocate_id')
        case = CaseRequest.objects.get(id=case_id)
        advocate = Advocate.objects.get(id=advocate_id)
        
        case.advocate = advocate
        case.save()
        
        messages.success(request, f"Advocate {advocate.first_name} {advocate.last_name} assigned successfully")
    return redirect('view_blockchain_cases')

def court_case_action(request, case_id, action):
    case = CaseRequest.objects.get(id=case_id)
    
    if action == "accept":
        case.status = "Court Accepted"
        messages.success(request, "Case has been formally accepted by the court.")
    elif action == "reject":
        case.status = "Court Rejected"
        messages.warning(request, "Case has been rejected by the court.")
        
    case.save()
    return redirect('view_blockchain_cases')
@login_required
def assign_case(request):
    # Fetch list of advocates for the assignment form
    advocates = Advocate.objects.filter(status="Approved").order_by('first_name')
    
    # Get current court info
    court = Court.objects.filter(user_id=request.user).first()

    if request.method == "POST":
        advocate_id = request.POST.get("advocate_id")
        case_title = request.POST.get("case_title")
        description = request.POST.get("description")
        case_file = request.FILES.get("case_file")

        # Create New Case Request (Internal Court Assignment)
        # Note: We are not linking to a specific User (Client) per user requirement
        case = CaseRequest.objects.create(
            case_title=case_title,
            description=description,
            advocate_id=advocate_id,
            court=court,
            court_location=court.location if court else "TBD",
            status="Case Assigned To Advocate",
            evidence_file=case_file
        )

        # ⛓️ Blockchain Integration
        if case.evidence_file and bh:
            try:
                # Read file content for hashing
                case.evidence_file.seek(0)
                file_content = case.evidence_file.read()
                evidence_hash, tx_hash = bh.store_evidence(file_content, case.id)
                
                # Save hashes to database
                case.evidence_hash = evidence_hash
                case.blockchain_txn_hash = tx_hash
                case.save()
                messages.success(request, f"Blockchain Evidence Seal Generated: {evidence_hash[:10]}...")
            except Exception as e:
                messages.warning(request, f"Blockchain recording error: {str(e)}")

        messages.success(request, f"Case #{case.id} assigned to Advocate successfully.")
        return redirect('assign_case')

    return render(request, 'assign_case.html', {
        'advocates': advocates
    })


def update_hearing_schedule(request):
    # Fetch the court instance for the logged-in user
    court = Court.objects.filter(user_id=request.user).first()
    
    if not court:
        return redirect('login')

    if request.method == "POST":
        case_id = request.POST.get('case_id')
        hearing_date = request.POST.get('hearing_date')
        new_status = request.POST.get('status')
        verdict = request.POST.get('verdict', "")
        notes = request.POST.get('notes', "")

        case = get_object_or_404(CaseRequest, id=case_id)
        
        # Update Case Status
        case.status = new_status
        case.save()

        # Create or update CourtHearing record
        CourtHearing.objects.create(
            case=case,
            hearing_date=hearing_date,
            verdict=verdict,
            notes=notes
        )

        messages.success(request, f"Hearing for CASE{case.id} scheduled successfully and status updated.")
        return redirect('update_hearing_schedule')

    # Fetch cases assigned to THIS COURT that are accepted or in trial
    cases = CaseRequest.objects.filter(
        court=court,
        status__in=["Court Accepted", "Under Trial", "Awaiting Verdict", "Case Disposed"]
    ).order_by('-created_at')

    
    return render(request, 'update_hearing_schedule.html', {
        'cases': cases
    })


def court_updates(request):
    # Ensure the logged-in user is an advocate
    advocate = Advocate.objects.filter(user_id=request.user).first()
    
    if not advocate:
        messages.error(request, "Access denied. Use advocate credentials.")
        return redirect('login')

    # Fetch cases assigned to THIS advocate
    # Incluldes trial-related statuses
    cases = CaseRequest.objects.filter(
        advocate=advocate,
        status__in=["Approved", "Case Assigned To Court", "Court Accepted", "Under Trial", "Awaiting Verdict", "Case Disposed"]
    ).order_by('-created_at')

    return render(request, 'court_updates.html', {
        'cases': cases
    })


@login_required
def view_case_progress(request):
    # Fetch cases submitted by the logged-in user
    cases = CaseRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'view_case_progress.html', {
        'cases': cases
    })


@login_required
def view_assigned_cases(request):
    # Ensure user is an advocate
    advocate = Advocate.objects.filter(user_id=request.user).first()
    if not advocate:
        messages.error(request, "Access denied. Use advocate credentials.")
        return redirect('login')

    # Fetch cases assigned BY COURT
    # Includes new, accepted, and rejected statuses to keep them visible
    cases = CaseRequest.objects.filter(
        advocate=advocate,
        status__in=["Case Assigned To Advocate", "Court Accepted", "Court Rejected"]
    ).order_by('-created_at')

    return render(request, 'view_assigned_cases.html', {
        'cases': cases
    })


@login_required
def advocate_court_action(request, case_id, action):
    case = get_object_or_404(CaseRequest, id=case_id)
    
    # Security check: ensure this advocate is assigned to the case
    advocate = Advocate.objects.filter(user_id=request.user).first()
    if case.advocate != advocate:
        messages.error(request, "Unauthorized action.")
        return redirect('view_assigned_cases')

    if action == "accept":
        case.status = "Court Accepted"
        messages.success(request, f"You have accepted CASE #{case.id}. It is now in the trial queue.")
    elif action == "reject":
        case.status = "Court Rejected"
        messages.warning(request, f"You have rejected CASE #{case.id}. The court will be notified.")
    
    case.save()
    return redirect('view_assigned_cases')

import google.generativeai as genai
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Configure API
GOOGLE_API_KEY = 'AIzaSyBP9urco5B-979To1oOas1iUMzmrdvx2FY'
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_gemini_response(prompt):
    system_instruction = (
        "You are a helpful legal assistant chatbot. Provide general legal guidance, "
        "especially focusing on women's rights, safety laws, workplace rights, and legal protections. "
        "Do not give definitive legal advice. Encourage consulting a qualified lawyer when necessary. "
        "Be clear, supportive, and informative."
    )

    final_prompt = f"{system_instruction}\n\nUser: {prompt}\nAssistant:"
    response = model.generate_content(final_prompt)

    return response.text if response else "Sorry, I couldn't generate a response right now."


@csrf_exempt
def chat_bot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        gemini_response = generate_gemini_response(user_message)

        return render(request, 'aichat.html', {
            'user_message': user_message,
            'response': gemini_response
        })

    return render(request, 'aichat.html')
@login_required
def court_assign_case(request):

    court = Court.objects.filter(user_id=request.user).first()
    if not court:
        messages.error(request, "Only courts can assign cases.")
        return redirect('login')

    advocates = Advocate.objects.filter(status="Approved")

    if request.method == "POST":
        case = CourtCase.objects.create(
            case_title=request.POST.get("case_title"),
            description=request.POST.get("description"),
            advocate_id=request.POST.get("advocate_id"),
            court=court,
            case_file=request.FILES.get("case_file")
        )

        messages.success(request, f"Court Case #{case.id} assigned successfully.")
        return redirect('court_will_assign_case')

    cases = CourtCase.objects.filter(court=court)

    return render(request, 'assign_case.html', {
        'advocates': advocates,
        'cases': cases
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CourtCase, Advocate


# 📄 View cases assigned to advocate
@login_required
def advocate_court_cases(request):

    advocate = Advocate.objects.filter(user_id=request.user).first()

    if not advocate:
        messages.error(request, "Access denied.")
        return redirect('login')

    # ✅ Handle status update POST
    if request.method == "POST":
        case_id = request.POST.get("case_id")
        new_status = request.POST.get("status")

        case = CourtCase.objects.get(id=case_id)

        if case.advocate == advocate:
            case.status = new_status
            case.save()
            messages.success(request, f"Case #{case.id} updated to {new_status}")

        return redirect('advocate_court_cases')

    cases = CourtCase.objects.filter(advocate=advocate).order_by('-created_at')

    return render(request, 'view_assigned_cases.html', {
        'cases': cases
    })

# ✅ Accept case
@login_required
def accept_court_case(request, case_id):

    advocate = Advocate.objects.filter(user_id=request.user).first()
    case = get_object_or_404(CourtCase, id=case_id)

    if case.advocate != advocate:
        messages.error(request, "Unauthorized action.")
        return redirect('advocate_court_cases')

    case.status = "Accepted"
    case.save()

    messages.success(request, f"Case #{case.id} accepted successfully.")
    return redirect('advocate_court_cases')


# ❌ Reject case
@login_required
def reject_court_case(request, case_id):

    advocate = Advocate.objects.filter(user_id=request.user).first()
    case = get_object_or_404(CourtCase, id=case_id)

    if case.advocate != advocate:
        messages.error(request, "Unauthorized action.")
        return redirect('advocate_court_cases')

    case.status = "Rejected"
    case.save()

    messages.warning(request, f"Case #{case.id} rejected.")
    return redirect('advocate_court_cases')