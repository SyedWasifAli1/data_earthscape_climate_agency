# views.py
import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import pymongo
import bcrypt
from .decorators import login_required
from bson.objectid import ObjectId
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from .forms import DatasetForm

# Mongo connection (settings.MONGO_URI and settings.MONGO_DB must be set)
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
users_collection = db["users"]
climate_collection = db["climate"]

# Home
def home(request):
    if request.session.get("username"):
        return redirect("dashboard")
    return render(request, "home.html")

def satellite_dashboard(request):
    """
    Renders the main Satellite Data page (with filters, search, etc.)
    """
    return render(request, "satellite.html")
def feedback(request):
    """
    Renders the main Satellite Data page (with filters, search, etc.)
    """
    return render(request, "feedback.html")
@login_required
def base(request):
    return render(request, "base.html")

# Register
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # role = request.POST.get("role", "user")
        if users_collection.find_one({"username": username}):
            messages.error(request, "❌ Username already exists!")
            return redirect("register")
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        users_collection.insert_one({
            "username": username,
            "password": hashed_pw,
            "role": "analyst"
        })
        messages.success(request, "✅ Registration successful! Please login.")
        return redirect("login")
    return render(request, "register.html")

# Login
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            request.session["username"] = username
            request.session["role"] = user.get("role", "user")
            if user.get("role") == "admin":
                return redirect("admin_dashboard")
            elif user.get("role") == "analyst":
                return redirect("analyst_dashboard")
            else:
                return redirect("dashboard")
        messages.error(request, "❌ Invalid username or password")
        return redirect("login")
    return render(request, "login.html")

@login_required
def admin_dashboard(request):
    if request.session.get("role") != "admin":
        messages.error(request, "❌ Access Denied!")
        return redirect("dashboard")
    return render(request, "admin_dashboard.html")

@login_required
def analyst_dashboard(request):
    if request.session.get("role") != "analyst":
        messages.error(request, "❌ Access Denied!")
        return redirect("dashboard")
    return render(request, "analyst_dashboard.html")

@login_required
def dashboard(request):
    role = request.session.get("role")
    if role == "admin":
        return redirect("admin_dashboard")
    elif role == "analyst":
        return redirect("analyst_dashboard")
    return render(request, "dashboard.html")

def logout(request):
    request.session.flush()
    messages.success(request, "✅ Logged out successfully")
    return redirect("login")


# -----------------------
# Dataset CRUD (MongoDB)
# -----------------------
# from django.shortcuts import render, redirect
# from django.conf import settings
# from django.contrib import messages
# from django.utils import timezone
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# from bson.objectid import ObjectId
# from .forms import DatasetForm
# from .decorators import login_required

# import pymongo

# client = pymongo.MongoClient(settings.MONGO_URI)
# db = client[settings.MONGO_DB]
# climate_collection = db["climate"]


@login_required
def dataset_list(request):
    datasets = list(climate_collection.find().sort("created_at", -1))
    for d in datasets:
        d["id"] = str(d.get("_id"))
        created = d.get("created_at")
        if created:
            try:
                d["created_at_display"] = created.strftime("%Y-%m-%d %H:%M")
            except Exception:
                d["created_at_display"] = str(created)
        else:
            d["created_at_display"] = ""
    return render(request, "datasets/list.html", {"datasets": datasets})


@login_required
def dataset_create(request):
    if request.method == "POST":
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            upload_file = request.FILES.get("upload_file")
            file_path = None
            if upload_file:
                filename = f"datasets/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload_file.name}"
                saved_name = default_storage.save(filename, ContentFile(upload_file.read()))
                try:
                    file_path = default_storage.url(saved_name)
                except Exception:
                    file_path = saved_name

            doc = {
                "name": data["name"],
                "source_type": data.get("source_type"),
                "file_format": data.get("file_format"),
                "upload_file": file_path,
                "data_source_url": data.get("data_source_url"),
                "date_start": data.get("date_start").isoformat() if data.get("date_start") else None,
                "date_end": data.get("date_end").isoformat() if data.get("date_end") else None,
                "is_realtime": data.get("is_realtime", False),
                "description": data.get("description"),
                "created_at": timezone.now()
            }
            climate_collection.insert_one(doc)
            messages.success(request, "✅ Dataset added successfully!")
            return redirect("dataset_list")
    else:
        form = DatasetForm()

    return render(request, "datasets/form.html", {"form": form, "title": "Add Dataset", "dataset": None})


@login_required
def dataset_update(request, pk):
    dataset = climate_collection.find_one({"_id": ObjectId(pk)})
    if not dataset:
        messages.error(request, "Dataset not found!")
        return redirect("dataset_list")

    if request.method == "POST":
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            upload_file = request.FILES.get("upload_file")
            file_path = dataset.get("upload_file")  # old file ka path

            # ✅ Agar naya file aya hai
            if upload_file:
                # Purana file delete kar do (agar exist karta hai)
                if file_path and default_storage.exists(file_path.replace(settings.DATASETS_URL, "datasets/")):
                    try:
                        default_storage.delete(file_path.replace(settings.DATASETS_URL, "datasets/"))
                    except Exception as e:
                        print("⚠️ File delete error:", e)

                # Naya file save karo
                filename = f"datasets/{timezone.now().strftime('%Y%m%d%H%M%S')}_{upload_file.name}"
                saved_name = default_storage.save(filename, ContentFile(upload_file.read()))
                try:
                    file_path = default_storage.url(saved_name)
                except Exception:
                    file_path = saved_name

            # ✅ Update document
            climate_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {
                    "name": data["name"],
                    "source_type": data.get("source_type"),
                    "file_format": data.get("file_format"),
                    "upload_file": file_path,  # old or new (jo bhi final hai)
                    "data_source_url": data.get("data_source_url"),
                    "date_start": data.get("date_start").isoformat() if data.get("date_start") else None,
                    "date_end": data.get("date_end").isoformat() if data.get("date_end") else None,
                    "is_realtime": data.get("is_realtime", False),
                    "description": data.get("description")
                }}
            )
            messages.success(request, "✅ Dataset updated successfully!")
            return redirect("dataset_list")

    else:
        form = DatasetForm(initial={
            "name": dataset.get("name", ""),
            "source_type": dataset.get("source_type", ""),
            "file_format": dataset.get("file_format", ""),
            "data_source_url": dataset.get("data_source_url", ""),
            "date_start": dataset.get("date_start", ""),
            "date_end": dataset.get("date_end", ""),
            "is_realtime": dataset.get("is_realtime", False),
            "description": dataset.get("description", ""),
        })

    return render(request, "datasets/form.html", {
        "form": form,
        "title": "Edit Dataset",
        "dataset": dataset
    })


@login_required
def dataset_detail(request, pk):
    dataset = climate_collection.find_one({"_id": ObjectId(pk)})
    if not dataset:
        messages.error(request, "Dataset not found!")
        return redirect("dataset_list")

    dataset["id"] = str(dataset.get("_id"))
    return render(request, "datasets/detail.html", {"dataset": dataset})


@login_required
def dataset_delete(request, pk):
    if request.method == "POST":
        try:
            dataset = climate_collection.find_one({"_id": ObjectId(pk)})
            if dataset:
                # File delete logic
                file_path = dataset.get("upload_file")

                if file_path:
                    # Agar sirf filename ya relative path store hai
                    if not os.path.isabs(file_path):
                        file_path = os.path.join(settings.DATASETS_ROOT, os.path.basename(file_path))

                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as fe:
                            messages.warning(request, f"⚠ File delete failed: {fe}")

                # DB record delete
                climate_collection.delete_one({"_id": ObjectId(pk)})
                messages.success(request, "🗑️ Dataset and file deleted successfully!")
            else:
                messages.error(request, "Dataset not found.")
        except Exception as e:
            messages.error(request, f"Delete failed: {e}")
    else:
        messages.error(request, "Invalid request method.")
    return redirect("dataset_list")
