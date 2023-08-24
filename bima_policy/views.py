from datetime import datetime
import random
from django.conf import settings
import ast
from storages.backends.s3boto3 import S3Boto3Storage
from django.http import HttpResponse
import subprocess
from dateutil.parser import parse
from itertools import chain
import pymongo
import boto3
from django.shortcuts import render
import json
import os
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View

from Bima.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_REGION, AWS_STORAGE_BUCKET_NAME, MEDIA_ROOT, TIME_ZONE
from .models import *
from .forms import *
from django.db.models import Q
# from bima_policy.static import vehicles


def get_id_from_session(request):
    id = request.session['id']
    return id


def is_user(request):
    return len(get_id_from_session(request)) >= 15


def Index(request):
    return render(request, 'index.html')

# DashBoardView


def dashboard(request):
    # print(get_profile_id(get_id_from_session(request)))    

    return render(request, 'dashboard.html')

    agentcount = Agents.objects.filter(status="Active").count()
    staffcount = StaffModel.objects.count()
    spcount = ServiceProvider.objects.count()
    if is_user(request):
        policycount = Policy.objects.count()
    else:
        print(get_id_from_session(request))

        policycount = Policy.objects.filter(
            employee=get_id_from_session(request)).count()

    print('total policycount :', policycount)

    return render(request, 'dashboard.html', {'agentcount': agentcount, 'staffcount': staffcount, 'spcount': spcount, 'totalpolicy': policycount})


def add_vehicles_data():
    return
    print('add_vehicles_data calling: ')

    with open('bima_policy//static//vehicle_data//vmake.txt', "r") as file:
        for line in file:
            print(line.strip())
            VehicleMake.objects.create(make=line.strip())
    with open('bima_policy//static//vehicle_data//vmodel.txt', "r") as file:
        for line in file:
            print(line.strip())
            VehicleModel.objects.create(model=line.strip())
    print('added')


def update_employee():
    return
    print('update_employee calling: ')

    # print(Policy.objects.filter(status='Active').count())
    # print(Policy.objects.filter(status= None).count())
    # Policy.objects.filter(status= None).update(status = 'Active')

    # print(Policy.objects.filter(employee='NEERAJ').count())
    # print(Policy.objects.filter(employee='SHABNAM').count())
    # print(Policy.objects.filter(employee='NISHA').count())

    # emp_data = Policy.objects.filter(employee = 'PANKAJ').update(employee = '6081E03886')
    # emp_data = Policy.objects.filter(employee = 'NEERAJ').update(employee = '8EBF59D741')
    # emp_data = Policy.objects.filter(employee = 'SHABNAM').update(employee = '1B98AFA2BF')
    # emp_data = Policy.objects.filter(employee = 'NISHA').update(employee = 'A0A954D4DD')

    print('done')

# LoginView


def login_form(request):
    return render(request, 'login.html')


def loginView(request):
    try:
        if request.method == 'POST':
            full_name = request.POST['full_name']
            password = request.POST['password']
            
            user = ProfileModel.objects.filter(full_name=full_name, password=password).first()
            user1 = Agents.objects.filter(login_id=full_name, password=password, status="Active").first()
            user2 = StaffModel.objects.filter(login_id=full_name, password=password).first()
            if user:
                # p = ProfileModel.objects.filter(full_name=full_name, password=password).first()
                # id = p.id
                request.session['id'] = user.id
                request.session['full_name'] = user.full_name

                # userr_ob = UserRole.objects.filter(profile_id=id)
                # if userr_ob:
                #     pass
                # else:
                #     UserRole.objects.create(profile_id_id=id, role='admin')

                request.session["role"] = "admin"
                # try:
                #     request.session['profile_image'] = user.profile_image.name
                #     print('profile_image: ',  user.profile_image.name)

                # except Exception as ex_u1:
                #     pass

                return redirect('bima_policy:dashboard')
            if user1:
                id = request.session['id'] = user1.login_id
                request.session['full_name'] = user1.full_name
                # user_ob = UserRole.objects.filter(agent_id=id).first()
                # role = user_ob.role
                request.session["role"] = "agent"
                return redirect('bima_policy:dashboard')
            if user2:
                request.session['id'] = user2.login_id
                request.session['staffname'] = user2.staffname
                request.session["role"] = "staff"

                return redirect('bima_policy:dashboard')
            return render(request, 'login.html', {'error_message': 'Invalid ID or Password!'})
    except (ProfileModel.DoesNotExist, Agents.DoesNotExist, StaffModel.DoesNotExist):
        error_message = 'Invalid ID or Password!'
        return render(request, 'login.html', {'error_message': error_message})



# ProfileView
def Profile(request):
    if request.method == "GET":
        try:
            data = ProfileModel.objects.filter(id=get_id_from_session(request))
            return render(request, 'profile/profile.html', {'data': data})
        except ProfileModel.DoesNotExist:
            return HttpResponse('Profile does not exist.')
    elif request.method == 'POST' and 'updpassword' in request.POST:
        try:
            profile = ProfileModel.objects.filter(
                id=get_id_from_session(request))
            password = request.POST['password']
            profile.update(password=password)
            return render(request, 'login.html', {'success_message': 'Password update successfully!'})
        except ProfileModel.DoesNotExist:
            return HttpResponse('Profile does not exist.')

    elif request.method == 'POST' and 'update_profile_image' in request.POST:
        try:
            profile_image = request.FILES.get('profile_image')
            if profile_image is not None:
                fspr = FileSystemStorage()
                fspr.save(profile_image.name, profile_image)
                profile = ProfileModel.objects.filter(
                    id=get_id_from_session(request))
                profile.update(profile_image=profile_image.name)
                print('Image updated')
                return render(request, 'login.html', {'success_message': 'Image update successfully!'})
        except ProfileModel.DoesNotExist:
            return HttpResponse('Profile does not exist.')


# UserView
def staffmanage(request):
    if request.method == 'GET':
        try:
            # data = StaffModel.objects.filter( profile_id=get_id_from_session(request))
            return render(request, 'user/user.html')

            data = StaffModel.objects.all()
            return render(request, 'user/user.html', {'data': data})
        except StaffModel.DoesNotExist:
            return render(request, 'user/user.html')
    else:
        if 'staff_add' in request.POST:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            staffname = request.POST['staffname']
            password = request.POST['password']
            StaffModel.objects.create(
                staffname=staffname, password=password, profile_id=data)
            return HttpResponseRedirect(request.path, ('staff'))


def staff_edit(request, id):
    print('staff edit calling: ')
    if request.method == 'GET':
        try:
            data = StaffModel.objects.filter(login_id=id)
            return render(request, 'user/user_edit.html', {'data': data})
        except StaffModel.DoesNotExist:
            return render(request, 'user/user_edit.html')
    else:
        if 'profile' in request.POST:
            StaffModel.objects.filter(login_id=id).update(
                staffname=request.POST['full_name'])
            print('staffname updated')
            return render(request, 'login.html', {'success_message': 'Name updated successfully!'})

        if 'security' in request.POST:
            StaffModel.objects.filter(login_id=id).update(
                password=request.POST['password'])
            print('password updated')
            return render(request, 'login.html', {'success_message': 'Password updated successfully!'})

        if 'update_profile_image' in request.POST:
            profile_image = request.FILES.get('profile_image')
            if profile_image is not None:
                fspr = FileSystemStorage()
                fspr.save(profile_image.name, profile_image)
                profile = StaffModel.objects.filter(
                    login_id=get_id_from_session(request))
                profile.update(profile_image=profile_image.name)
                StaffModel.objects.filter(login_id=id).update(
                    profile_image=profile_image.name)
                print('profile_image updated')
                return render(request, 'login.html', {'success_message': 'Image updated successfully!'})
        return redirect('bima_policy:staff')


def staff_delete(request, id):
    print('\ndelete_staff calling:')
    # print(id)
    try:
        StaffModel.objects.filter(login_id=id).delete()
        print('staff user deleted\n')
        return redirect('bima_policy:staff')
    except Exception as e:
        print(str(e))
        return HttpResponse(str(e))

# ProfileView


def bank_details(request):
    if request.method == "GET":
        try:
            data = {}
            pdata = ProfileModel.objects.filter(
                id=get_id_from_session(request))
            bdata = BankDetail.objects.filter(
                profile_id_id=get_id_from_session(request))
            return render(request, 'profile/bank_details.html', {'pdata': pdata, 'bdata': bdata})
        except BankDetail.DoesNotExist:
            return render(request, 'profile/bank_details.html')
    else:
        try:
            if "bankadd" in request.POST:
                data = ProfileModel.objects.get(
                    id=get_id_from_session(request))
                beneficiary_name = request.POST['beneficiary_name']
                acc_no = request.POST['account_number']
                bank_name = request.POST['bank_name']
                BankDetail.objects.create(
                    beneficiary_name=beneficiary_name, acc_no=acc_no, bank_name=bank_name, profile_id=data)
                return HttpResponseRedirect(request.path, ('bank_det'))
        except ProfileModel.DoesNotExist:
            return HttpResponse('error')
    return HttpResponseRedirect(request.path, ('bank_det'))


def delete_bank_details(request, id):
    if request.method == "GET":
        return redirect('bima_policy:bank_det')
    else:
        if "delete" in request.POST:
            # obj=BankDetail.objects.filter(id=id)
            # obj.delete()
            get_object_or_404(BankDetail, id=id).delete()
            return redirect('bima_policy:bank_det')


def change_password_old(request):
    print("change_password method calling:")
    if request.method == 'POST' and 'updpassword' in request.POST:
        profile = ProfileModel.objects.filter(id=get_id_from_session(request))
        password = request.POST['password']
        profile.update(password=password)


def change_password(request):
    print("change_password method calling:")
    print('id: ', get_id_from_session(request))

    data = json.loads(request.POST['data'])
    # print(data)
    splited_array = str(data).split('|')
    old_pass = splited_array[0]
    new_pass = splited_array[1]

    print('old pass: ', old_pass)
    print('new pass: ', new_pass)

    context = {
        "status": "error occurred!"
    }

    if is_user(request):
        profile = ProfileModel.objects.filter(id=get_id_from_session(request))
        profile_pass = ProfileModel.objects.filter(
            id=get_id_from_session(request)).values()[0]['password']

        if profile_pass == old_pass:
            print('old match found:')
            profile.update(password=new_pass)
            context['status'] = 'Password updated!'
            print('new password set')
        else:
            context['status'] = 'Your Last Password is Incorrect!'
            print('incorrect password')

    else:
        staff = StaffModel.objects.filter(
            login_id=get_id_from_session(request))
        staff_pass = StaffModel.objects.filter(
            login_id=get_id_from_session(request)).values()[0]['password']

        if staff_pass == old_pass:
            print('old match found:')
            staff.update(password=new_pass)
            context['status'] = 'Password updated!'
            print('new password set')
        else:
            context['status'] = 'Your Last Password is Incorrect!'
            print('incorrect password')

    return JsonResponse(context)


def profile_photo(request):
    print("profile_photo method calling:")
    print('id: ', get_id_from_session(request))

    data = json.loads(request.POST['data'])

    print('profile photo: ', data)

    context = {
        "status": "error occurred!"
    }

    if is_user(request):
        profile = ProfileModel.objects.filter(id=get_id_from_session(request))

        profile.update(profile_image=data)
        context['status'] = 'Password updated!'
        print('profile picture changed')

    return JsonResponse(context)


# RTOView
def rto_list_old(request):
    if request.method == "GET":
        data = RtoConversionModel.objects.filter(
            profile_id_id=get_id_from_session(request))
        return render(request, 'rto/RTO.html', {'data': data})
    if request.method == "POST" and 'rto_add' in request.POST:
        data = ProfileModel.objects.get(id=get_id_from_session(request))
        rtoseries = request.POST['rtoseries']
        rtoreturn = request.POST['rtoreturn']
        RtoConversionModel.objects.create(
            rto_series=rtoseries, rto_return=rtoreturn, profile_id=data)
        return redirect('bima_policy:rto')


def rto_list(request):
    print('rto_list calling: ')

    if request.method == "GET":
        # data = RtoTable.objects.create(rto_state = 'test', rto_city = 'test', rto_code = 'test')
        data = RtoTable.objects.all().values()

        print(data.__len__())
        return render(request, 'rto/RTO.html', {'data': data})
    if request.method == "POST" and 'rto_add' in request.POST:
        data = ProfileModel.objects.get(id=get_id_from_session(request))
        rtoseries = request.POST['rtoseries']
        rtoreturn = request.POST['rtoreturn']
        RtoConversionModel.objects.create(
            rto_series=rtoseries, rto_return=rtoreturn, profile_id=data)
        return redirect('bima_policy:rto')


def update_rto(request, id):
    print('update_rto calling: ')
    return HttpResponse('No RTOs deleted/updated!')
    data = {}
    if request.method == "GET":
        data = RtoTable.objects.filter(id=id)
        return render(request, 'RTO.html', {'data': data})
    if request.method == 'POST':
        if "delete" in request.POST:
            item = get_object_or_404(RtoTable, id=id)
            item.delete()
            print('RTO deleted: ', item)
            return redirect('bima_policy:rto')


# InsuranceView
def ins_comp(request):
    print('ins_comp')
    if request.method == "GET":
        try:
            # data = InsuranceCompany.objects.filter(profile_id=get_id_from_session(request))
            data = InsuranceCompany.objects.all()
            return render(request, 'insurancecompany/insurance_comp.html', {'data': data})
        except ProfileModel.DoesNotExist:
            return render(request, 'insurancecompany/insurance_comp.html')
    elif 'company_add' in request.POST:
        try:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            ins_name = request.POST['inscomp_name']
            status = request.POST['status']
            InsuranceCompany.objects.create(
                comp_name=ins_name, status=status, profile_id=data)
            return redirect('bima_policy:ins_comp')
        except ProfileModel.DoesNotExist:
            return HttpResponseRedirect(request.path, ('bank_det'))


def ins_del(request, id):
    if request.method == 'POST' and 'delete' in request.POST:
        data = InsuranceCompany.objects.filter(id=id)
        data.delete()
        return redirect('bima_policy:ins_comp')


def write_vehicle_data():
    return
    # Connect to MongoDB
    client = pymongo.MongoClient(
        "mongodb+srv://bhavi:Rqw7dAxrzY3UUj1S@experiya.bi2f9gh.mongodb.net/?retryWrites=true&w=majority")

    # client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["vehicle_data"]
    make_col = db["make"]
    model_col = db["model"]
    # Open the text file and read the record
    with open('bima_policy//static//vehicle_data//vmake.txt', "r") as file:
        for line in file:
            record = line.strip()
            record_json = {"make": record}
            make_col.insert_one(record_json)
    print('done')

    with open('bima_policy//static//vehicle_data//vmodel.txt', "r") as file:
        for line in file:
            record = line.strip()
            record_json = {"model": record}
            model_col.insert_one(record_json)

    print('done')


def write_vehicle_data2():
    # return;
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["experiya"]
    make_col = db["make"]
    model_col = db["model"]
    # Open the text file and read the record
    with open('bima_policy//static//vehicle_data//vmake.txt', "r") as file:
        for line in file:
            record = line.strip()
            record_json = {"make": record}
            make_col.insert_one(record_json)
    print('done')

    with open('bima_policy//static//vehicle_data//vmodel.txt', "r") as file:
        for line in file:
            record = line.strip()
            record_json = {"model": record}
            model_col.insert_one(record_json)

    print('done')


def write_vehicle_data2_list_type():

    return

    # Open the text file and read the record
    with open('bima_policy//static//vehicle_data//vmake.txt', "r") as file:
        with open('bima_policy//static//vehicle_data//vmake2.txt', "w") as file2:
            for line in file:
                record = line.strip()
                record = '"' + record + '"' + ','

                file2.write(record)
    print('done')

    with open('bima_policy//static//vehicle_data//vmodel.txt', "r") as file:
        with open('bima_policy//static//vehicle_data//vmodel2.txt', "w") as file2:
            for line in file:
                record = line.strip()
                record = '"' + record + '"' + ','

                file2.write(record)
    print('done')


def write_vehicle_d():
    return
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["experiya"]
    # make_col = db["company"]
    make_col = db["rto"]

    with open('bima_policy//static//vehicle_data//no.txt', "r") as file:
        for line in file:
            record = line.strip()
            if record == '':
                pass
            else:
                rc = record.split(',')
                # record_json = {"vehicle_code": rc[0],
                #                "make": rc[1],
                #                "model": rc[2],
                #                "variant": rc[3],
                #                "body_type": rc[4],
                #                "seating_capacity": rc[5],
                #                "power": rc[6],
                #                "cubic_capacity": rc[7],
                #                "gvw": rc[8],
                #                "fuel_type": rc[9],
                #                "wheels_count": rc[10],
                #                "abs": rc[11],
                #                "air_bags": rc[12],
                #                "length": rc[13],
                #                "ex_showroom_price": rc[14],
                #                "price_year": rc[15],
                #                "production": rc[16],
                #                "manufacturing": rc[17],
                #                "vehicle_type": rc[18]
                #                }
                record_json = {"registered_city_name": rc[0],
                               "registered_state_name": rc[1],
                               "rto_code": rc[2]
                               }
                make_col.insert_one(record_json)
                print(record_json)

    print('done')


def read_vehical_model_data(request):
    print('read_vehical_model_data')
    return
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.ExperiyaBook
    collection = db.model

    # Retrieve data from MongoDB collection
    vehicle_data = list(collection.find())

    # print(data)
    # Pass data to template for rendering
    return redirect('bima_policy:vehi')


def read_vehicle_data_file():
    # return;
    make_list = []
    model_list = []
    cat_list = []
    # Open the text file and read the record
    # with open('bima_policy//static//vehicle_data//vmake.txt', "r") as file:
    #     for line in file:
    #         make_list.append(line.strip())

    print('done')

    with open('bima_policy//static//vehicle_data//vmodel.txt', "r") as file:
        for line in file:
            model_list.append(line.strip())

    # with open('bima_policy//static//vehicle_data//vcat.txt', "r") as file:
    #     for line in file:
    #         cat_list.append(line.strip())

    context = {
        "make": make_list,
        "model": model_list
    }

    return context


def read_all_vehical_data():
    # Connect to MongoDB
    # client = pymongo.MongoClient("mongodb+srv://bhavi:Rqw7dAxrzY3UUj1S@experiya.bi2f9gh.mongodb.net/?retryWrites=true&w=majority")
    client = pymongo.MongoClient('mongodb://localhost:27017/')

    db = client.ExperiyaBook
    make_col = db.make
    # model_col = db.model

    # Retrieve data from MongoDB collection
    context = {
        "make": list(make_col.find())
        # "model" : list(model_col.find())
    }

    # print(data)
    # Pass data to template for rendering
    return context


def read_all_vehical_data_file():
    # Connect to MongoDB
    # client = pymongo.MongoClient("mongodb+srv://bhavi:Rqw7dAxrzY3UUj1S@experiya.bi2f9gh.mongodb.net/?retryWrites=true&w=majority")
    client = pymongo.MongoClient('mongodb://localhost:27017/')

    db = client.ExperiyaBook
    make_col = db.make
    # model_col = db.model

    # Retrieve data from MongoDB collection
    context = {
        "make": list(make_col.find())
        # "model" : list(model_col.find())
    }

    # print(data)
    # Pass data to template for rendering
    return context


def product_view(request):

    print("product_view method calling")
    # mylist = zip(datamn, data)

    if request.method == "GET":
        try:
            products = Product.objects.all().values()
            return render(request, 'product/product.html', {"products": products})
        except(Product.DoesNotExist):
            return render(request, 'product/product.html')
    else:
        if 'product_add' in request.POST:
            Product.objects.create(
                name=request.POST['product_name'], status='Active')

            return redirect('bima_policy:product_view')


def add_product(request, name):
    try:
        print('add_product method')
        print(name)
        product = Product.objects.create(name=name)
        print('product created: ', product)
        return redirect('bima_policy:product_view')
    except Exception as ex:
        print(ex)
        return HttpResponse('Error Occurred in delete_product method! Report this problem to your Admin: ' + str(ex))


def delete_product(request, name):
    try:
        print('delete_product method')
        print(name)
        Product.objects.filter(name=name).delete()
        print('product deleted: ')
        return redirect('bima_policy:product_view')
    except Exception as ex:
        print(ex)
        return HttpResponse('Error Occurred in delete_product method! Report this problem to your Admin: ' + str(ex))


def vehicle_view(request):

    print("vehicle_view method calling")

    if request.method == "GET":
        try:
            data_cat = VehicleCategory.objects.all().values()

            makes = VehicleMake.objects.values('make')
            models = VehicleModel.objects.values('model')

            context = {
                "data_cat": data_cat,
                "makes": makes,
                "models": models
            }

            # mylist = zip(datamn, data)
            return render(request, 'vehicle/vehicle.html', context)
        except(delete_vehicle_make.DoesNotExist, VehicleModel.DoesNotExist, VehicleCategory.DoesNotExist):
            return render(request, 'vehicle/vehicle.html')
    else:

        p = ProfileModel.objects.get(id=get_id_from_session(request))
        if 'mb_add' in request.POST:
            VehicleMake.objects.create(
                make=request.POST['makeby'], status=request.POST['mbstatus'])
            return redirect('bima_policy:vehi')
        elif 'vm_add' in request.POST:
            VehicleModel.objects.create(
                model=request.POST['model'], status=request.POST['vmstatus'])
            return redirect('bima_policy:vehi')
        elif 'vc_add' in request.POST:
            VehicleCategory.objects.create(
                category=request.POST['category'], status=request.POST['vcstatus'], profile_id=p)
            return redirect('bima_policy:vehi')

        return redirect('bima_policy:vehi')


def delete_vehicle_category(request, id):
    print('delete_vehicle_category method')

    print(id)

    try:
        VehicleCategory.objects.get(category=id).delete()
        return redirect('bima_policy:vehi')
    except Exception as ex:
        print(ex)
        return HttpResponse('Error Occurred in delete_vehicle_category method!')


def delete_vehicle_model(request, id):
    print('delete_vehicle_moel method')

    print(id)

    try:
        VehicleModel.objects.get(model=id).delete()
        return redirect('bima_policy:vehi')
    except Exception as ex:
        print(ex)
        return HttpResponse('Error Occurred in delete_vehicle_model method!')


def delete_vehicle_make(request, id):
    print('delete_vehicle_make method')

    print(id)

    try:
        VehicleMake.objects.get(make=id).delete()
        return redirect('bima_policy:vehi')
    except Exception as ex:
        print(ex)
        return HttpResponse('Error Occurred in delete_vehicle_make method!')


# ServiceProviderView


def service_provider(request):
    if request.method == "GET":
        try:
            # brokerdata = BrokerCode.objects.filter( profile_id=get_id_from_session(request))
            brokerdata = BrokerCode.objects.all()
            data = ServiceProvider.objects.all()
            return render(request, 'serviceprovider/service_provider.html', {'data': data, 'brokerdata': brokerdata})
        except (ServiceProvider.DoesNotExist, BrokerCode.DoesNotExist):
            return render(request, 'serviceprovider/service_provider.html')
    else:
        if 'code_add' in request.POST:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            code = request.POST['code']
            status = request.POST['status']
            BrokerCode.objects.create(
                code=code, status=status, profile_id=data)
            return redirect('bima_policy:service_p')


def del_broker_code(request, id):
    BrokerCode.objects.filter(id=id).delete()
    return redirect('bima_policy:service_p')


def add_sp(request):
    if request.method == "GET":
        data = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))
        return render(request, 'serviceprovider/add_sp.html', {'data': data})
    else:
        if 'subbtn' in request.POST:
            p = ProfileModel.objects.get(id=get_id_from_session(request))
            data = ServiceProvider.objects.filter(
                profile_id_id=get_id_from_session(request))
            full_name = request.POST['full_name']
            email_id = request.POST['email_id']
            phone = request.POST['phone']
            address = request.POST['address']
            state = request.POST['state']
            city = request.POST['city']
            gstin = request.POST['gstin']
            pan = request.POST['pan']
            ServiceProvider.objects.create(full_name=full_name, email_id=email_id, mob_no=phone,
                                           address=address, state=state, city=city, GSTIN=gstin, PAN=pan, profile_id=p)
            return redirect('bima_policy:service_p')


def delete_sp(request, id):
    if request.method == 'POST':
        ServiceProvider.objects.get(id=id).delete()
        return redirect('bima_policy:service_p')


def edit_sp(request, id):
    if request.method == 'GET':
        data = ServiceProvider.objects.filter(id=id)
        return render(request, 'serviceprovider/edit_sp.html', {'data': data})
    elif request.method == 'POST' and 'subbtn' in request.POST:
        # pd=ProfileModel.objects.get(id=get_id_from_session(request))
        data = ServiceProvider.objects.filter(id=id)
        full_name = request.POST['full_name']
        email_id = request.POST['email_id']
        phone = request.POST['phone']
        address = request.POST['address']
        state = request.POST['state']
        city = request.POST['city']
        gstin = request.POST['gstin']
        pan = request.POST['pan']
        data.update(full_name=full_name, email_id=email_id, mob_no=phone,
                    address=address, state=state, city=city, GSTIN=gstin, PAN=pan)
        return redirect('bima_policy:service_p')
    return redirect('bima_policy:service_p')


def get_profile_id(id):
    login_id = ''
    try:
        login_id = ProfileModel.objects.get(id=id).id
        return login_id
    except Exception as ex:
        pass
    try:
        login_id = Agents.objects.get(login_id=id, status="Active").profile_id
        return login_id
    except Exception as ex:
        pass
    try:
        login_id = StaffModel.objects.get(login_id=id).profile_id
        return login_id
    except Exception as ex:
        pass

    return ''


def get_user_name(request):
    try:
        name = ProfileModel.objects.filter(
            id=get_id_from_session(request)).values()[0]['full_name']
        return name
    except Exception as ex:
        pass
    try:
        name = StaffModel.objects.filter(
            login_id=get_id_from_session(request)).values().first()['staffname']
        return name
    except Exception as ex:
        pass
    try:
        name = Agents.objects.filter(login_id=get_id_from_session(
            request), status="Active").values().first()['full_name']
        return name
    except Exception as ex:
        pass

    return ''


def get_user_role(request):
    try:
        name = ProfileModel.objects.filter(
            id=get_id_from_session(request)).values()[0]['full_name']
        return 'admin'
    except Exception as ex:
        pass
    try:
        name = StaffModel.objects.filter(
            login_id=get_id_from_session(request)).values().first()['staffname']
        return 'user'
    except Exception as ex:
        pass
    try:
        name = Agents.objects.filter(login_id=get_id_from_session(
            request), status="Active").values().first()['full_name']
        return 'agent'
    except Exception as ex:
        pass

    return ''


def fetch_vehicle_data():
    # with open('bima_policy//static//vehicle_data//vcat.txt', 'rb') as f:
    #     vcat = f.readlines()
    with open('bima_policy//static//vehicle_data//vmake.txt', 'rb') as f:
        vmake = f.readlines()
    with open('bima_policy//static//vehicle_data//vmodel.txt', 'rb') as f:
        vmodel = f.readlines()
    vdata = {
        # "vcat": vcat,
        "vmake": vmake,
        "vmodel": vmodel
    }
    return vdata


def fix_special_chars_from_coverage_type(vm, data):
    # vehicle coverage type from policy
    vm = vm.lower()
    if vm.__contains__('+'):
        vm = vm.replace('+', ' ')

    # vehicle coverage type from payout
    vmp = data[0]['coverage_type'].lower()
    if vmp.__contains__('+'):
        vmp = vmp.replace('+', ' ')

    if vmp.__contains__(vm):
        return data
    else:
        return None


def fix_special_chars_from_vehicle_model(vm, data):
    # vehicle model from policy
    vm = vm.lower()
    if vm.__contains__('/'):
        vm = vm.replace('/', ' ')
    if vm.__contains__('+'):
        vm = vm.replace('+', ' ')
    if vm.__contains__('*'):
        vm = vm.replace('*', ' ')

    # vehicle model from payout
    vmp = data[0]['vehicle_model'].lower()
    if vmp.__contains__('/'):
        vmp = vmp.replace('/', ' ')
    if vmp.__contains__('+'):
        vmp = vmp.replace('+', ' ')
    if vmp.__contains__('*'):
        vmp = vmp.replace('*', ' ')

    if vmp.__contains__(vm):
        return data
    else:
        return None


def fix_special_chars_from_coverage_typep(vm, data):
    # vehicle coverage type from policy
    vm = vm.lower()
    if vm.__contains__('+'):
        vm = vm.replace('+', ' ')

    # vehicle coverage type from payout
    obj = Payout.objects.filter(payoutid=data.payoutid).values()
    vmp = obj[0]['coverage_type'].lower()
    if obj is not None:
        if vmp.__contains__('+'):
            vmp = vmp.replace('+', ' ')

    if vmp.__contains__(vm):
        return data
    else:
        return None


def fix_special_chars_from_vehicle_modelp(vm, data):
    # vehicle model from policy
    vm = vm.lower()
    if vm.__contains__('/'):
        vm = vm.replace('/', ' ')
    if vm.__contains__('+'):
        vm = vm.replace('+', ' ')
    if vm.__contains__('*'):
        vm = vm.replace('*', ' ')

    # vehicle model from payout
    obj = Payout.objects.filter(payoutid=data.payoutid).values()
    vmp = obj[0]['vehicle_model'].lower()
    if obj is not None:
        if vmp.__contains__('/'):
            vmp = vmp.replace('/', ' ')
        if vmp.__contains__('+'):
            vmp = vmp.replace('+', ' ')
        if vmp.__contains__('*'):
            vmp = vmp.replace('*', ' ')

    if vmp.__contains__(vm):
        return data
    else:
        return None


class create_policy(View):
    def get(self, request):
        print('create_policy get method')

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values():
            agents.append(ag['posp_code'] + ' | ' + ag['full_name'])
        # agents.sort()
        # print(agents)

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting service_providers name
        service_providers = []
        for provider in ServiceProvider.objects.values('full_name'):
            service_providers.append(provider['full_name'])
        service_providers.sort()

        # getting office_codes
        broker_codes = []
        for code in BrokerCode.objects.values('code'):
            broker_codes.append(code['code'])
        broker_codes.sort()

        # getting vehicle categories name and sort them.
        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = VehicleMake.objects.values('make')
        models = VehicleModel.objects.values('model')

        # getting bqps
        bqps = []
        for bqp in BQP.objects.values('name'):
            bqps.append(bqp['name'])
        bqps.sort()

        context = {
            "agents": agents,
            "insurers": insurers,
            "service_providers": service_providers,
            "broker_codes": broker_codes,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models,
            "bqps": bqps,
            "is_user": is_user(request),
            "user_id": get_id_from_session(request),
            "user_name": get_user_name(request),
            "is_motor_form": True
        }

        return render(request, 'policylist/policy_list.html', context)
        # return render(request, 'policylist/policy_list.html', {"user_info": user_info, "vdata": context, "data_vc": data_vc, 'is_motor_form': True, 'data_ag': ag,  'data_sp': data_sp, 'data_bc': data_bc, 'data_ins': data_ins, 'data_bqp': data_bqp})

    def post(self, request):
        try:
            print('create_policy post method')
            id = get_profile_id(get_id_from_session(request))
            print('id: ', id)

            profile_id = ProfileModel.objects.get(id=id)

            proposal_no = str.strip(request.POST['proposal_no'])
            policy_no = str.strip(request.POST['policy_no'])
            customer_name = str.strip(request.POST['customer_name'])
            insurance_company = request.POST['insurance_company']
            sp_name = request.POST['sp_name']
            sp_brokercode = request.POST['sp_brokercode']
            registration_no = str.strip(request.POST['registration_no'])
            rto_state = request.POST['rto_state']
            rto_city = str.strip(request.POST['rto_city'])
            vehicle_makeby = str.strip(request.POST['vehicle_makeby'])
            vehicle_model = str.strip(request.POST['vehicle_model'])
            vehicle_catagory = request.POST['vehicle_catagory']
            vehicle_fuel_type = request.POST['vehicle_fuel_type']
            mfg_year = request.POST['mfg_year']
            addon = request.POST['addon']
            ncb = request.POST['ncb']
            try:
                cubic_capacity = request.POST['cubic_capacity']
            except Exception as ex:
                cubic_capacity = ''
            gvw = request.POST['gvw']
            seating_capacity = request.POST['seating_capacity']
            coverage_type = request.POST['coverage_type']
            policy_type = request.POST['policy_type']
            cpa = request.POST['cpa']
            risk_start_date = request.POST['risk_start_date']
            risk_end_date = request.POST['risk_end_date']
            issue_date = request.POST['issue_date']
            insured_age = request.POST['insured_age']
            policy_term = request.POST['policy_term']
            bqp = request.POST['bqp']
            pos = request.POST['pos']

            employee = get_id_from_session(request)

            try:
                remark = request.POST['remark']
            except Exception as ex:
                remark = ''

            OD_premium = str.strip(request.POST['od'])
            TP_terrorism = str.strip(request.POST['tpt'])
            net = request.POST['net']
            gst_amount = request.POST['gst']
            try:
                gst_gcv_amount = request.POST['gstt']
            except Exception as ex:
                gst_gcv_amount = 0

            total = request.POST['total']
            payment_mode = request.POST['payment_mode']

            proposal = request.FILES.get('proposal')
            mandate = request.FILES.get('mandate')
            policy = request.FILES.get('policy')
            previous_policy = request.FILES.get('previous_policy')
            pan_card = request.FILES.get('pan_card')
            aadhar_card = request.FILES.get('aadhar_card')
            vehicle_rc = request.FILES.get('vehicle_rc')
            inspection_report = request.FILES.get('inspection_report')

            fspr = FileSystemStorage()

            if proposal is not None:
                fspr.save(proposal.name, proposal)
            if mandate is not None:
                fspr.save(mandate.name, mandate)
            if policy is not None:
                fspr.save(policy.name, policy)
            if previous_policy is not None:
                fspr.save(previous_policy.name, previous_policy)
            if pan_card is not None:
                fspr.save(pan_card.name, pan_card)
            if aadhar_card is not None:
                fspr.save(aadhar_card.name, aadhar_card)
            if vehicle_rc is not None:
                fspr.save(vehicle_rc.name, vehicle_rc)
            if inspection_report is not None:
                fspr.save(inspection_report.name, inspection_report)

            pol = Policy.objects.create(profile_id=profile_id, proposal_no=proposal_no, policy_no=policy_no,  customer_name=customer_name, insurance_company=insurance_company, sp_name=sp_name,
                                        sp_brokercode=sp_brokercode,  registration_no=registration_no,
                                        rto_state=rto_state, rto_city=rto_city,  vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model, vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type,
                                        mfg_year=mfg_year,
                                        addon=addon, ncb=ncb, cubic_capacity=cubic_capacity, gvw=gvw, seating_capacity=seating_capacity, coverage_type=coverage_type, policy_type=policy_type, cpa=cpa,
                                        risk_start_date=risk_start_date,
                                        risk_end_date=risk_end_date, issue_date=issue_date, insured_age=insured_age, policy_term=policy_term, payment_mode=payment_mode, bqp=bqp, pos=pos,
                                        employee=employee, proposal=proposal, mandate=mandate,
                                        OD_premium=OD_premium,  TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount,
                                        gst_gcv_amount=gst_gcv_amount,  total=total,
                                        policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card, vehicle_rc=vehicle_rc, inspection_report=inspection_report,
                                        remark=remark)

            print('policy created: ', pol)

            if vehicle_catagory == 'TWO WHEELER' or vehicle_catagory == 'TWO WHEELER SCOOTER' or vehicle_catagory == 'TWO WHEELER BIKE':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(cubic_capacity__icontains=cubic_capacity) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    if data:
                        data = fix_special_chars_from_vehicle_model(
                            vehicle_model, data)
                        data = fix_special_chars_from_coverage_type(
                            coverage_type, data)

                except Exception as ex:
                    print(ex)

            if vehicle_catagory == 'TWO WHEELER COMMERCIAL':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(cubic_capacity__icontains=cubic_capacity) &
                                                 Q(seating_capacity__icontains=seating_capacity) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'PRIVATE CAR' or vehicle_catagory == 'TRADE RISK':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(cubic_capacity__icontains=cubic_capacity) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'GCV-PUBLIC CARRIER OTHER THAN 3 W':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(gvw__icontains=gvw) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    # data = fix_special_chars_from_coverage_type(coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == '3 WHEELER PCV':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(seating_capacity__icontains=seating_capacity) &
                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == '3 WHEELER GCV-PUBLIC CARRIER':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(seating_capacity__icontains=seating_capacity) &
                                                 Q(gvw__icontains=gvw) &
                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'TAXI 4 WHEELER':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(cubic_capacity__icontains=cubic_capacity) &
                                                 Q(seating_capacity__icontains=seating_capacity) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'BUS AND OTHERS':
                try:
                    reg = registration_no[0:4]
                    seating_capacity = int(request.POST['seating_capacity1'])
                    cap = seating_capacity
                    print('cap ', cap)

                    if cap < 5:
                        cap = 'BELOW 5'
                    elif cap > 4 and cap < 8:
                        cap = '5-7'
                    elif cap > 6 and cap < 13:
                        cap = '7-12'
                    elif cap > 11 and cap < 19:
                        cap = '12-18'
                    elif cap > 18:
                        cap = 'ABOVE 18'

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(seating_capacity__icontains=cap) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'MISC-D SPECIAL VEHICLE':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(seating_capacity__icontains=cap) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            elif vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME' or vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
                try:
                    reg = registration_no[0:4]

                    data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                                 Q(sp_name__icontains=sp_name) &
                                                 Q(sp_brokercode__icontains=sp_brokercode) &
                                                 Q(vehicle_makeby__icontains=vehicle_makeby) &

                                                 Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                                 Q(mfg_year__icontains=mfg_year) &
                                                 Q(rto_city__icontains=reg) &
                                                 Q(addon__icontains=addon) &
                                                 Q(ncb__icontains=ncb) &
                                                 Q(seating_capacity__icontains=cap) &

                                                 Q(policy_type__icontains=policy_type) &
                                                 Q(policy_term__icontains=policy_term) &
                                                 Q(cpa__contains=cpa)).values()

                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

                except Exception as ex:
                    print(ex)

            print('payout data: ', data)

            if data:
                return render(request, 'policylist/list_apply_payout.html', {'data': data, 'policyid': pol.policyid})
            else:
                return render(request, 'policylist/policy_entry_list.html', {'data': Policy.objects.filter(policyid=pol.policyid).values()})

        except Exception as ex:
            print('ex ', ex)
            return HttpResponse("Error occurred! When Creating New Policy! Contact Your Admin", ex)


def new_entryy(request, data):
    try:
        print('new_entry post method')
        print('current_time: ', datetime.now())

        print(request['data'])
        id = get_profile_id(get_id_from_session(request))

        profile_id = ProfileModel.objects.get(id=id)
        proposal_no = str.strip(request.POST['proposal_no'])
        policy_no = str.strip(request.POST['policy_no'])
        customer_name = str.strip(request.POST['customer_name'])
        insurance_company = request.POST['insurance_company']
        sp_name = request.POST['sp_name']
        sp_brokercode = request.POST['sp_brokercode']
        registration_no = str.strip(request.POST['registration_no'])
        rto_state = request.POST['rto_state']
        rto_city = str.strip(request.POST['rto_city'])
        vehicle_makeby = str.strip(request.POST['vehicle_makeby'])
        vehicle_model = str.strip(request.POST['vehicle_model'])
        vehicle_catagory = request.POST['vehicle_catagory']
        vehicle_fuel_type = request.POST['vehicle_fuel_type']
        mfg_year = request.POST['mfg_year']
        addon = request.POST['addon']
        ncb = request.POST['ncb']
        try:
            cubic_capacity = request.POST['cubic_capacity']
        except Exception as ex:
            cubic_capacity = ''
        gvw = request.POST['gvw']
        seating_capacity = request.POST['seating_capacity']
        coverage_type = request.POST['coverage_type']
        policy_type = request.POST['policy_type']
        cpa = request.POST['cpa']
        risk_start_date = request.POST['risk_start_date']
        risk_end_date = request.POST['risk_end_date']
        issue_date = request.POST['issue_date']
        insured_age = request.POST['insured_age']
        policy_term = request.POST['policy_term']
        bqp = request.POST['bqp']
        pos = request.POST['pos']
        employee = get_id_from_session(request)
        try:
            remark = request.POST['remark']
        except Exception as ex:
            remark = ''
        OD_premium = str.strip(request.POST['od'])
        TP_terrorism = str.strip(request.POST['tpt'])
        net = request.POST['net']
        gst_amount = request.POST['gst']
        try:
            gst_gcv_amount = request.POST['gstt']
        except Exception as ex:
            gst_gcv_amount = 0
        total = request.POST['total']
        payment_mode = request.POST['payment_mode']

        proposal = request.FILES.get('proposal')
        mandate = request.FILES.get('mandate')
        policy = request.FILES.get('policy')
        previous_policy = request.FILES.get('previous_policy')
        pan_card = request.FILES.get('pan_card')
        aadhar_card = request.FILES.get('aadhar_card')
        vehicle_rc = request.FILES.get('vehicle_rc')
        inspection_report = request.FILES.get('inspection_report')

        fspr = FileSystemStorage()

        if proposal is not None:
            fspr.save(proposal.name, proposal)
        if mandate is not None:
            fspr.save(mandate.name, mandate)
        if policy is not None:
            fspr.save(policy.name, policy)
        if previous_policy is not None:
            fspr.save(previous_policy.name, previous_policy)
        if pan_card is not None:
            fspr.save(pan_card.name, pan_card)
        if aadhar_card is not None:
            fspr.save(aadhar_card.name, aadhar_card)
        if vehicle_rc is not None:
            fspr.save(vehicle_rc.name, vehicle_rc)
        if inspection_report is not None:
            fspr.save(inspection_report.name, inspection_report)

        pol = Policy.objects.create(profile_id=profile_id, proposal_no=proposal_no, policy_no=policy_no,  customer_name=customer_name, insurance_company=insurance_company, sp_name=sp_name,
                                    sp_brokercode=sp_brokercode,  registration_no=registration_no,
                                    rto_state=rto_state, rto_city=rto_city,  vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model, vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type,
                                    mfg_year=mfg_year,
                                    addon=addon, ncb=ncb, cubic_capacity=cubic_capacity, gvw=gvw, seating_capacity=seating_capacity, coverage_type=coverage_type, policy_type=policy_type, cpa=cpa,
                                    risk_start_date=risk_start_date,
                                    risk_end_date=risk_end_date, issue_date=issue_date, insured_age=insured_age, policy_term=policy_term, payment_mode=payment_mode, bqp=bqp, pos=pos,
                                    employee=employee, proposal=proposal, mandate=mandate,
                                    OD_premium=OD_premium,  TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount,
                                    gst_gcv_amount=gst_gcv_amount,  total=total,
                                    policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card, vehicle_rc=vehicle_rc, inspection_report=inspection_report,
                                    remark=remark)

        print('policy created: ', pol)

        data = Policy.objects.filter(policyid=pol.policyid).values()

        print('current_time: ', datetime.now())

        return render(request, 'policylist/policy_entry_list.html', {'data': data})

        if vehicle_catagory == 'TWO WHEELER' or vehicle_catagory == 'TWO WHEELER SCOOTER' or vehicle_catagory == 'TWO WHEELER BIKE':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(cubic_capacity__icontains=cubic_capacity) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                if data:
                    data = fix_special_chars_from_vehicle_model(
                        vehicle_model, data)
                    data = fix_special_chars_from_coverage_type(
                        coverage_type, data)

            except Exception as ex:
                print(ex)

        if vehicle_catagory == 'TWO WHEELER COMMERCIAL':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(cubic_capacity__icontains=cubic_capacity) &
                                             Q(seating_capacity__icontains=seating_capacity) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'PRIVATE CAR' or vehicle_catagory == 'TRADE RISK':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(cubic_capacity__icontains=cubic_capacity) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'GCV-PUBLIC CARRIER OTHER THAN 3 W':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(gvw__icontains=gvw) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                # data = fix_special_chars_from_coverage_type(coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == '3 WHEELER PCV':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(seating_capacity__icontains=seating_capacity) &
                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == '3 WHEELER GCV-PUBLIC CARRIER':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(seating_capacity__icontains=seating_capacity) &
                                             Q(gvw__icontains=gvw) &
                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'TAXI 4 WHEELER':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(cubic_capacity__icontains=cubic_capacity) &
                                             Q(seating_capacity__icontains=seating_capacity) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'BUS AND OTHERS':
            try:
                reg = registration_no[0:4]
                seating_capacity = int(request.POST['seating_capacity1'])
                cap = seating_capacity
                print('cap ', cap)

                if cap < 5:
                    cap = 'BELOW 5'
                elif cap > 4 and cap < 8:
                    cap = '5-7'
                elif cap > 6 and cap < 13:
                    cap = '7-12'
                elif cap > 11 and cap < 19:
                    cap = '12-18'
                elif cap > 18:
                    cap = 'ABOVE 18'

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(seating_capacity__icontains=cap) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'MISC-D SPECIAL VEHICLE':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(seating_capacity__icontains=cap) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        elif vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME' or vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__icontains=insurance_company) &
                                             Q(sp_name__icontains=sp_name) &
                                             Q(sp_brokercode__icontains=sp_brokercode) &
                                             Q(vehicle_makeby__icontains=vehicle_makeby) &

                                             Q(vehicle_fuel_type__icontains=vehicle_fuel_type) &
                                             Q(mfg_year__icontains=mfg_year) &
                                             Q(rto_city__icontains=reg) &
                                             Q(addon__icontains=addon) &
                                             Q(ncb__icontains=ncb) &
                                             Q(seating_capacity__icontains=cap) &

                                             Q(policy_type__icontains=policy_type) &
                                             Q(policy_term__icontains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

                data = fix_special_chars_from_vehicle_model(
                    vehicle_model, data)
                data = fix_special_chars_from_coverage_type(
                    coverage_type, data)

            except Exception as ex:
                print(ex)

        print('payout data: ', data)
        if data:
            return render(request, 'policylist/list_apply_payout.html', {'data': data, 'policyid': pol.policyid})
        else:
            return render(request, 'policylist/policy_entry_list.html', {'data': Policy.objects.filter(policyid=pol.policyid).values()})

    except Exception as ex:
        print('ex ', ex)
        return HttpResponse("Error occurred! When Creating New Policy! Contact Your Admin", ex)


class create_policy_non_motor(View):
    def get(self, request):
        print('create_policy Non get')

        # getting products name and sorts them.
        products = []
        for p in Product.objects.values('name'):
            products.append(p['name'])
        products.sort()

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values():
            agents.append(ag['posp_code'] + ' | ' + ag['full_name'])
        # print(agents)

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting service_providers name
        service_providers = []
        for provider in ServiceProvider.objects.values('full_name'):
            service_providers.append(provider['full_name'])
        service_providers.sort()

        # getting office_codes
        broker_codes = []
        for code in BrokerCode.objects.values('code'):
            broker_codes.append(code['code'])
        broker_codes.sort()

        # getting bqps
        bqps = []
        for bqp in BQP.objects.values('name'):
            bqps.append(bqp['name'])
        bqps.sort()

        context = {
            "products": products,
            "agents": agents,
            "insurers": insurers,
            "service_providers": service_providers,
            "broker_codes": broker_codes,
            "bqps": bqps,
            "is_user": is_user(request),
            "user_id": get_id_from_session(request),
            "user_name": get_user_name(request),
            "is_motor_form": False
        }

        return render(request, 'policylist/policy_list.html', context)

    def post(self, request):
        print('create_policy non post')
        profile_id = ProfileModel.objects.get(
            id=get_profile_id(get_id_from_session(request)))

        product_name = request.POST['product_name']
        policy_type = request.POST['policy_type']
        proposal_no = request.POST['proposal_no']
        policy_no = request.POST['policy_no']
        customer_name = request.POST['customer_name']
        insurance_company = request.POST['insurance_company']
        sp_name = request.POST['sp_name']
        sp_brokercode = request.POST['sp_brokercode']

        risk_start_date = request.POST['risk_start_date']
        risk_end_date = request.POST['risk_end_date']
        issue_date = request.POST['issue_date']
        policy_term = request.POST['policy_term']
        bqp = request.POST['bqp']
        pos = request.POST['pos']
        employee = get_id_from_session(request)
        try:
            remark = request.POST['remark']
        except Exception as ex:
            remark = ''

        OD_premium = request.POST['od']
        TP_terrorism = request.POST['tpt']
        net = request.POST['net']
        gst_amount = request.POST['gst']
        total = request.POST['total']
        payment_mode = request.POST['payment_mode']

        proposal = request.FILES.get('proposal')
        mandate = request.FILES.get('mandate')
        policy = request.FILES.get('policy')
        previous_policy = request.FILES.get('previous_policy')
        pan_card = request.FILES.get('pan_card')
        aadhar_card = request.FILES.get('aadhar_card')
        inspection_report = request.FILES.get('inspection_report')
        fspr = FileSystemStorage()
        fsm = FileSystemStorage()
        fsp = FileSystemStorage()
        fspp = FileSystemStorage()
        fspc = FileSystemStorage()
        fsac = FileSystemStorage()

        fsis = FileSystemStorage()
        if proposal is not None:
            fspr.save(proposal.name, proposal)
        if mandate is not None:
            fsm.save(mandate.name, mandate)
        if policy is not None:
            fsp.save(policy.name, policy)
        if previous_policy is not None:
            fspp.save(previous_policy.name, previous_policy)
        if pan_card is not None:
            fspc.save(pan_card.name, pan_card)
        if aadhar_card is not None:
            fsac.save(aadhar_card.name, aadhar_card)

        if inspection_report is not None:
            fsis.save(inspection_report.name, inspection_report)

        # print('policy type ', policy_type )
        data = Policy.objects.create(profile_id=profile_id, product_name=product_name, policy_type=policy_type,
                                     proposal_no=proposal_no, policy_no=policy_no, customer_name=customer_name,
                                     insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                                     risk_start_date=risk_start_date,
                                     risk_end_date=risk_end_date, issue_date=issue_date,
                                     policy_term=policy_term,  bqp=bqp, pos=pos,
                                     employee=employee, proposal=proposal, mandate=mandate,
                                     policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card, inspection_report=inspection_report,
                                     OD_premium=OD_premium,  TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount, total=total,
                                     payment_mode=payment_mode, remark=remark)
        print('pol data ', data)

        data = Policy.objects.filter(policyid=data.policyid).values()

        return render(request, 'policylist/policy_entry_list.html', {'data': data})


def apply_policy(request, id):
    try:
        print('apply_policy method calling: ')

        data = Policy.objects.get(policyid=id)
        print('first data is: ', data)

        if data.vehicle_catagory == 'TWO WHEELER' or data.vehicle_catagory == 'TWO WHEELER SCOOTER' or data.vehicle_catagory == 'TWO WHEELER BIKE':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(cubic_capacity__icontains=data.cubic_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]
                # print('data1 is ', data1)

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'TWO WHEELER COMMERCIAL':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(cubic_capacity__icontains=data.cubic_capacity) &
                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'PRIVATE CAR' or data.vehicle_catagory == 'TRADE RISK':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(cubic_capacity__icontains=data.cubic_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'GCV-PUBLIC CARRIER OTHER THAN 3 W':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(gvw__icontains=data.gvw) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == '3 WHEELER PCV':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == '3 WHEELER GCV-PUBLIC CARRIER':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(gvw__icontains=data.gvw) &
                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'TAXI 4 WHEELER':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &
                                              Q(cubic_capacity__icontains=data.cubic_capacity) &
                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'BUS AND OTHERS':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &

                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'MISC-D SPECIAL VEHICLE':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &

                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        elif data.vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME' or data.vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
                                              Q(sp_name__icontains=data.sp_name) &
                                              Q(sp_brokercode__icontains=data.sp_brokercode) &
                                              Q(vehicle_makeby__icontains=data.vehicle_makeby) &

                                              Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
                                              Q(mfg_year__icontains=data.mfg_year) &
                                              Q(rto_city__icontains=reg) &
                                              Q(addon__icontains=data.addon) &
                                              Q(ncb__icontains=data.ncb) &

                                              Q(seating_capacity__icontains=data.seating_capacity) &

                                              Q(policy_type__icontains=data.policy_type) &
                                              Q(policy_term__icontains=data.policy_term) &
                                              Q(cpa__contains=data.cpa))[0]

                if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
                    if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                        agent_od_reward = float(data1.agent_od_reward)
                        agent_od_amount = round(
                            (float(data.OD_premium) * agent_od_reward) / 100, 2)
                        agent_tp_reward = float(data1.agent_tp_reward)
                        agent_tp_amount = round(
                            (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                        # Self payout
                        self_od_reward = float(data1.self_od_reward)
                        self_od_amount = round(
                            (float(data.OD_premium) * self_od_reward) / 100, 2)
                        self_tp_reward = float(data1.self_tp_reward)
                        self_tp_amount = round(
                            (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                        data = Policy.objects.filter(policyid=id)

                        data.update(agent_od_reward=agent_od_reward,
                                    agent_od_amount=agent_od_amount,
                                    agent_tp_reward=agent_tp_reward,
                                    agent_tp_amount=agent_tp_amount,

                                    self_od_reward=self_od_reward,
                                    self_od_amount=self_od_amount,
                                    self_tp_reward=self_tp_reward,
                                    self_tp_amount=self_tp_amount)

            except Exception as ex:
                print(ex)

        data = Policy.objects.filter(policyid=id).values()

        return render(request, 'policylist/policy_entry_list.html', {'data': data})

        return redirect('bima_policy:create_policy')
    except Exception as ex:
        print(ex)
        return HttpResponse('apply_policy method originated folowing error: ' + ex)

# import datetime


def policy_entry(request):
    print('\npolicy_entry method')
    return render(request, 'policylist/policy_entry_list.html')

    try:
        print('\npolicy_entry method')

        return render(request, 'policylist/policy_entry_list.html')

        agents = []
        for ag in Agents.objects.filter(status="Active").values():
            agents.append(ag['posp_code'] + ' | ' + ag['full_name'])
        # print(agents)

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting vehicle categories name and sort them.
        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = []
        for make in VehicleMake.objects.values('make'):
            makes.append(make['make'])
        models = []
        for model in VehicleModel.objects.values('model'):
            models.append(model['model'])

        current_datetime = datetime.now()
        # print(current_datetime)

        if is_user(request):
            # data = Policy.objects.order_by('-created_at').values()[:5]
            data = Policy.objects.filter(created_at=current_datetime).values()

        else:
            data = Policy.objects.filter(
                created_at=current_datetime, employee=get_id_from_session(request)).values()

        context = {
            "agents": agents,
            "insurers": insurers,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models,
            "data": data,
            "is_user": is_user(request),
            "user_name": get_user_name(request)
        }

        return render(request, 'policylist/policy_entry_list.html', context)

    except Exception as ex:
        print(ex)
        return HttpResponse('Error in policy_entry ' + str(ex))


def count_objects(request):
    print('\ncount_objects calling ')

    staffcount = StaffModel.objects.count()
    agentcount = Agents.objects.filter(status="Active").count()
    spcount = ServiceProvider.objects.count()
    policycount = Policy.objects.count()

    data = {
        "staffcount": staffcount,
        "agentcount": agentcount,
        "spcount": spcount,
        "policycount": policycount
    }

    return JsonResponse({'data': data})


def fetch_key(request):
    # print('\nfetch_key calling ')

    keys = {
        "accessKeyId": AWS_ACCESS_KEY_ID,
        "secretAccessKey": AWS_SECRET_ACCESS_KEY,
        "region": AWS_ACCESS_KEY_REGION,
        "BUCKET_NAME": AWS_STORAGE_BUCKET_NAME
    }

    # print(keys)

    return JsonResponse({'data': keys})


def fetch_policyId(request):
    print('\nfetch_policyId calling ')

    policy = list(Policy.objects.filter(
        policyid=request.GET.get('data'))  .values())

    return JsonResponse({'data': policy})


def fetch_records(request):
    print('\nfetch_records calling ')

    data = request.GET.get('data').split('|')
    # print(data)

    # get from todays
    if data[0] == '':
        if is_user(request):
            records = Policy.objects.filter(created_at=datetime.now()).values()
        else:
            records = Policy.objects.filter(employee=get_id_from_session(
                request), created_at=datetime.now()).values()

        return JsonResponse({'data': list(records)})

    # get mixed
    if data[0] == 'filter_data':
        agents = []
        for ag in Agents.objects.filter(status="Active").values():
            agents.append(ag['posp_code'] + ' | ' + ag['full_name'])

        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = list(VehicleMake.objects.values('make'))
        models = list(VehicleModel.objects.values('model'))

        filter_data = {'agents': agents, 'insurers': insurers,
                       'vcats': vehicle_categories, 'vmakes': makes, 'vmodels': models}

        return JsonResponse({'filter_data': filter_data})

    if data[0] == 'posp':
        agents = Agents.objects.filter(status="Active").values()
        return JsonResponse({'posp': list(agents)})

    if data[0] == 'staffs':
        staffs = StaffModel.objects.values()
        return JsonResponse({'data': list(staffs)})

    if data[0] == 'slabs':
        data = Slab.objects.values()
        return JsonResponse({'data': list(data)})

    if data[0] == 'insurers':
        data = InsuranceCompany.objects.values()
        return JsonResponse({'data': list(data)})

    if data[0] == 'products':
        data = Product.objects.values()
        return JsonResponse({'data': list(data)})

    if data[0] == 'sps':
        data = list(ServiceProvider.objects.values())
        bc = list(BrokerCode.objects.values())
        return JsonResponse({'data': data, 'bc': bc})

    if data[0] == 'vehicles':
        category = list(VehicleCategory.objects.values())
        makes = list(VehicleMake.objects.values())
        models = list(VehicleModel.objects.values())

        data = {'category': category, 'makes': makes, 'models': models}

        return JsonResponse({'data': data})

    if data[0] == 'employee':
        data = get_user_name(request)
        return JsonResponse({'data': data})

    if data[0] == 'motor_option':
        category = list(VehicleCategory.objects.values())
        makes = list(VehicleMake.objects.values())
        models = list(VehicleModel.objects.values())

        data = {'category': category, 'makes': makes, 'models': models}
        posp = list(Agents.objects.filter(status="Active").values())
        ins = list(InsuranceCompany.objects.values())
        sp = list(ServiceProvider.objects.values())
        bc = list(BrokerCode.objects.values())

        employee = get_user_name(request)

        return JsonResponse({'data': data, 'posp': posp, 'ins': ins, 'sp': sp, 'bc': bc, 'employee': employee})

    if data[0] == 'non_motor_option':
        products = list(Product.objects.values())
        posp = list(Agents.objects.filter(status="Active").values())
        ins = list(InsuranceCompany.objects.values())
        sp = list(ServiceProvider.objects.values())
        bc = list(BrokerCode.objects.values())

        employee = get_user_name(request)

        return JsonResponse({'products': products, 'posp': posp, 'ins': ins, 'sp': sp, 'bc': bc, 'employee': employee})

    d1_array = data[0].split('-')
    d2_array = data[1].split('-')

    year = d1_array[2]
    month = d1_array[1]
    day = d1_array[0]
    date1 = year + "-" + month + "-" + day

    year = d2_array[2]
    month = d2_array[1]
    day = d2_array[0]
    date2 = year + "-" + month + "-" + day

    date_string = date1
    date_string2 = date2
    date_format = '%Y-%m-%d'

    date1 = datetime.strptime(date_string, date_format).date()
    date2 = datetime.strptime(date_string2, date_format).date()

    if is_user(request):
        records = Policy.objects.filter(
            issue_date__gte=date1, issue_date__lte=date2).values()
    else:
        records = Policy.objects.filter(employee=get_id_from_session(
            request), issue_date__gte=date1, issue_date__lte=date2).values()

    return JsonResponse({'data': list(records)})


def fetch_record(request):
    print('\nfetch record calling ')

    data = request.GET.get('data')
    print(data)

    # search for proposal no
    record = list(Policy.objects.filter(proposal_no__iexact=data).values())
    if record.__len__() > 0:
        return JsonResponse({'record': record})

    # search for policy no
    record = list(Policy.objects.filter(policy_no__iexact=data).values())
    if record.__len__() > 0:
        return JsonResponse({'record': record})

    # search for customer name
    record = list(Policy.objects.filter(
        customer_name__icontains=data).values())
    if record.__len__() > 0:
        return JsonResponse({'record': record})

    return JsonResponse({'message': "Not found!"})


def fetch_mix_records(request):
    print('\nfetch_mix_records calling ')

    data = request.GET.get('data').split('|')
    print(data)

    agents = []
    for ag in Agents.objects.filter(status="Active").values():
        agents.append(ag['posp_code'] + ' | ' + ag['full_name'])

    return JsonResponse({'agents': agents})


def fetch_all(request):
    print('\nfetch_all calling ')

    # policy
    if is_user(request):
        policy = list(Policy.objects.filter(
            issue_date=datetime.now()).values())
        # policy = list(Policy.objects.order_by('-issue_date').values()[:5])
        # policy = list(Policy.objects.order_by('-policyid').values() )
    else:
        policy = list(Policy.objects.filter(employee=get_id_from_session(
            request), issue_date=datetime.now()).values())

    # agents = list(Agents.objects.filter(status="Active").values())
    agents = list(Agents.objects.filter(status="Active").values('login_id', 'posp_code', 'registration_code', 'full_name', 'gender', 'email_id', 'mob_no', 'address', 'state', 'city', 'pincode', 'rural_urban', 'slab', 'GSTIN', 'account_no', 'ifsc_code', 'bank_name', 'basic_qualification', 'aadhar_card', 'pan_card', 'training_certificate', 'appointment_certificate', 'agreement_certificate', 'bank_details', 'created_by', 'status' ))
    insurers = list(InsuranceCompany.objects.values())
    sp = list(ServiceProvider.objects.values())
    bc = list(BrokerCode.objects.values())
    products = list(Product.objects.values())

    vc = list(VehicleCategory.objects.values())
    makes = list(VehicleMake.objects.values())
    models = list(VehicleModel.objects.values())
    staff = list(StaffModel.objects.values('login_id', 'staffname', 'status'))
    

    data = {
        "employee": get_user_name(request),
        "dashboard_details": {"staffcount": staff.__len__(), "agentcount": agents.__len__(), "spcount": sp.__len__(), "policycount": Policy.objects.count()},
        "entry_list": policy,
        "agents": agents,
        "insurers": insurers,
        "sps": sp,
        "bc": bc,
        "products": products,
        "vehicles": {'category': vc, 'makes': makes, 'models': models},
        "staffs": staff
    }
    return JsonResponse({'data': data})


def policy_saerch_entry(request, id):
    try:
        print('policy_saerch_entry method')
        parsed_id = str(id)
        print('id: ', parsed_id)
        if parsed_id.__contains__("--"):
            parsed_id = parsed_id.replace("--", "/")

        agent_list = []
        datag = Agents.objects.filter(status="Active").values('full_name')
        for ag in datag:
            agent_list.append(ag['full_name'])

        datacat_list = []
        data_cat = VehicleCategory.objects.all().values()
        for vc in data_cat:
            datacat_list.append(vc["category"])

        data = Policy.objects.filter(policy_no=parsed_id).values()

        policyid_list = []
        for item in data:
            policyid_list.append(item['policyid'])

        return render(request, 'policylist/policy_entry_list.html', {"policyid_list": policyid_list, "agent_list": agent_list, "vdata": '', "data_cat": datacat_list, 'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as ex:
        print(ex)
        return HttpResponse('Error occurred in policy_saerch_entry:')


def policy_entry_filter(request,  data):
    try:
        print('policy_entry_filter method')

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values('full_name'):
            agents.append(ag['full_name'])
        agents.sort()

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting vehicle categories name and sort them.
        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = []
        for make in VehicleMake.objects.values('make'):
            makes.append(make['make'])
        models = []
        for model in VehicleModel.objects.values('model'):
            models.append(model['model'])

        tmp_data = json.loads(data)

        print('request data: ', tmp_data)

        if str(tmp_data).__contains__('-'):

            if len(tmp_data) == 1:
                print('into 1st lane')
                tdata = tmp_data[0]
                print('tdata [0] ', tdata[0])
                print('tdata [1] ', tdata[1])

                d1_array = tdata[0].split('-')
                d2_array = tdata[1].split('-')

                year = d1_array[2]
                month = d1_array[1]
                day = d1_array[0]
                date1 = year + "-" + month + "-" + day

                year = d2_array[2]
                month = d2_array[1]
                day = d2_array[0]
                date2 = year + "-" + month + "-" + day

                print('date 1: ', date1)
                print('date 2: ', date2)

                if is_user(request):
                    data = Policy.objects.filter(Q(issue_date__gte=date1) & Q(
                        issue_date__lte=date2)).order_by('-policyid').values()
                else:
                    data = Policy.objects.filter(Q(employee=get_id_from_session(request)) & Q(
                        issue_date__gte=date1) & Q(issue_date__lte=date2)).order_by('-policyid').values()

                policyid_list = []
                for item in data:
                    # print('item is: ',  item['policyid'])
                    policyid_list.append(item['policyid'])

                # return render(request, 'policylist/policy_entry_list.html', {"agent_list": agent_list,  "policyid_list": policyid_list,  "data_cat": datacat_list, "vdata": context, 'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})

            if len(tmp_data) == 2:
                print('into 2nd lane')
                print('into 2nd lane')

                # date section
                tdata = tmp_data[0]

                d1_array = tdata[0].split('-')
                d2_array = tdata[1].split('-')

                year = d1_array[2]
                month = d1_array[1]
                day = d1_array[0]
                date1 = year + "-" + month + "-" + day

                year = d2_array[2]
                month = d2_array[1]
                day = d2_array[0]
                date2 = year + "-" + month + "-" + day

                print('date 1: ', date1)
                print('date 2: ', date2)

                # other filter section
                # print('tmdata [1] : ', tmp_data[1])

                if is_user(request):
                    data = Policy.objects.filter(Q(issue_date__gte=date1) & Q(
                        issue_date__lte=date2)).order_by('-policyid').values()
                else:
                    data = Policy.objects.filter(Q(employee=get_id_from_session(request)) & Q(
                        issue_date__gte=date1) & Q(issue_date__lte=date2)).order_by('-policyid').values()

                print(tmp_data[1][0])
                data = filter_other_details(tmp_data[1], data)

                data = list(chain(*data))

                policyid_list = []
                for item in data:
                    # print('item is: ',  item['policyid'])
                    policyid_list.append(item['policyid'])

                if len(data) > 0:
                    # data = data[0]
                    pass

                else:
                    data = None

                # return render(request, 'policylist/policy_entry_list.html', {"policyid_list": policyid_list, "agent_list": agent_list, "data_cat": datacat_list, "vdata": context, 'select_length': '25', 'period': 'TODAY', 'data': data,  'is_user': is_user(request)})

            if len(tmp_data) == 3:
                print('into 3rd lane')

                # date section
                tdata = tmp_data[0]

                d1_array = tdata[0].split('-')
                d2_array = tdata[1].split('-')

                year = d1_array[2]
                month = d1_array[1]
                day = d1_array[0]
                date1 = year + "-" + month + "-" + day

                year = d2_array[2]
                month = d2_array[1]
                day = d2_array[0]
                date2 = year + "-" + month + "-" + day

                print('date 1: ', date1)
                print('date 2: ', date2)

                payout_option = tmp_data[2]
                print('payout: ', payout_option)

                if payout_option == 'y':
                    if is_user(request):
                        data = Policy.objects.filter(Q(issue_date__gte=date1) & Q(
                            issue_date__lte=date2) & Q(agent_od_reward="")).order_by('-policyid').values()
                    else:
                        data = Policy.objects.filter(Q(employee=get_id_from_session(request)) & Q(issue_date__gte=date1) & Q(
                            issue_date__lte=date2) & Q(agent_od_reward="")).order_by('-policyid').values()

                    # data = Policy.objects.order_by('-policyid').filter(Q(issue_date__gte=date1 ) & Q(issue_date__lte=date2) & Q(agent_od_reward="")  ).values()
                else:
                    if is_user(request):
                        data = Policy.objects.filter(Q(issue_date__gte=date1) & Q(
                            issue_date__lte=date2)).order_by('-policyid').values()
                    else:
                        data = Policy.objects.filter(Q(employee=get_id_from_session(request)) & Q(
                            issue_date__gte=date1) & Q(issue_date__lte=date2)).order_by('-policyid').values()

                    # data = Policy.objects.order_by('-policyid').filter(Q(issue_date__gte=date1 ) & Q(issue_date__lte=date2) ).values()

                print(tmp_data[1][0])
                data = filter_other_details(tmp_data[1], data)

                data = list(chain(*data))

                policyid_list = []
                for item in data:
                    # print('item is: ',  item['policyid'])
                    policyid_list.append(item['policyid'])

                if len(data) > 0:
                    # data = data[0]
                    pass
                else:
                    data = None

        else:
            print('tmp_data is', tmp_data)

            # tmp_data is [['15', '5', '15', '15'], "['66B9786', '16DCC32']"]

            print('tmp_data[0] ',  tmp_data[0])
            print('tmp_data[1] ',  tmp_data[1])

            payout_values = {

                "aod": tmp_data[0][0],
                "atp": tmp_data[0][1],
                "sod": tmp_data[0][2],
                "stp": tmp_data[0][3]
            }

            print('payout_values ', payout_values)

            updated_policy_list = []

            for id in str(tmp_data[1]).split(','):
                try:
                    tid = id.replace('[', '').replace(']', '').replace(
                        "'", '').replace("'", '').strip()
                    print(tid)
                    tmp_dataa = Policy.objects.get(policyid=tid)
                    print('tmp_data: ', tmp_dataa)

                    # Agent payout
                    aod = float(payout_values['aod'])
                    agent_od_amount = round(
                        (float(tmp_dataa.OD_premium) * aod) / 100, 2)
                    atp = float(payout_values['atp'])
                    agent_tp_amount = round(
                        (float(tmp_dataa.TP_terrorism) * atp) / 100, 2)

                    # # Self payout
                    sod = float(payout_values['sod'])
                    self_od_amount = round(
                        (float(tmp_dataa.OD_premium) * sod) / 100, 2)
                    stp = float(payout_values['stp'])
                    self_tp_amount = round(
                        (float(tmp_dataa.TP_terrorism) * stp) / 100, 2)

                    ddata = Policy.objects.filter(policyid=tid)

                    print('ddata: ', ddata)

                    ddata.update(agent_od_reward=aod,
                                 agent_od_amount=agent_od_amount,
                                 agent_tp_reward=atp,
                                 agent_tp_amount=agent_tp_amount,

                                 self_od_reward=sod,
                                 self_od_amount=self_od_amount,
                                 self_tp_reward=stp,
                                 self_tp_amount=self_tp_amount)
                    print('Done')
                    updated_policy_list.append(ddata.values())

                except Exception as exc:
                    print(exc)

            print('updated list length: ', len(updated_policy_list))

            data = list(chain(*updated_policy_list))

        context = {
            "agents": agents,
            "insurers": insurers,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models,
            "data": data,
            "policyid_list": policyid_list,
            "is_user": is_user(request)
        }

        return render(request, 'policylist/policy_entry_list.html', context)

    except Exception as ex:
        return HttpResponse('Error occurred in policy_entry_filter: ' + str(ex))


def policy_entry_date_filter(request, data, filter_payout='n'):
    try:
        print('policy_entry_date_filter method')
        # request data:  [['01/04/2023', '30/04/2023']]

        str_data = str(data)
        # ['07/05/2023', '07/05/2023'] = yesterday
        str_data = str_data.replace('/', '-').split(',')
        # print('str_data ', str_data)

        sd1 = str_data[0].replace("[", '').split('-')
        sd2 = str_data[1].replace("]", '').split('-')
        # print('sd1 ', sd1)
        # date1
        d = parse(sd1[0]).day
        m = parse(sd1[1]).month
        y = parse(sd1[2]).year
        # date2
        d2 = parse(sd2[0]).day
        m2 = parse(sd2[1]).month
        y2 = parse(sd2[2]).year

        # print('sd2 ', sd2)
        sdv = str_data[0].strip().split('-')
        # print('sdv ', sdv)
        # print(sdv  ["'01", '04', "2023'"])
        year = sdv[2]
        month = sdv[1]
        day = sdv[0]
        date1 = year + "-" + month + "-" + day
        date1 = date1.replace("'", "").replace("[", "").replace("]", "").replace(
            "[[", "").replace("]]", "").replace("'", "")

        # sdv = str_data[1].strip().replace("[", '').split('-')
        sdv = str_data[1].strip().split('-')
        # print('sdv ', sdv)
        # print(sdv  ["'01", '04', "2023'"])
        year = sdv[2]
        month = sdv[1]
        day = sdv[0]
        date2 = year + "-" + month + "-" + day
        date2 = date2.replace("'", "").replace("[", "").replace("]", "").replace(
            "[[", "").replace("]]", "").replace("'", "")

        # date1 = datetime(y, m, d)
        # date1 = datetime(y, d, m)
        # date2 = datetime(y2, m2, d2)
        print('date 1: ', date1)
        print('date 2: ', date2)

        tmp_adv_list = []

        print('filter_payoutis :', filter_payout)

        if is_user(request):
            # data = Policy.objects.filter(issue_date__gte='01/04/2023').filter(issue_date__lte='30/04/2023').values()
            # data = Policy.objects.filter(issue_date__gte='2023-04-01').filter(issue_date__lte='2023-04-30').values()
            if filter_payout == "y":
                # data = Policy.objects.filter(issue_date__gte=date1).filter(issue_date__lte=date2).values()
                data = Policy.objects.filter(Q(issue_date__gte=date1) & Q(
                    issue_date__lte=date2) & Q(agent_od_reward="")).values()
            else:
                data = Policy.objects.filter(
                    Q(issue_date__gte=date1) & Q(issue_date__lte=date2)).values()

            tmp_adv_list.append(data)
        else:
            # data = Policy.objects.filter(employee=get_id_from_session(request)).filter(issue_date__gte=date1).filter(issue_date__lte=date2).values()
            data = Policy.objects.filter(
                employee=get_id_from_session(request)).values()

        data = list(chain(*tmp_adv_list))

        return data

    except Exception as ex:
        print('error occurred in policy_entry_date_filter: ', ex)
        return ex


def filter_other_details(data, f_data):
    print('')
    print('filter_other_details calling:')
    print('data: ', data)
    # print('data: ', f_data)

    qs_list_temp = []
    qs_list = []

    str_dataa = str(data)

    # filter for ins
    if str_dataa.__contains__('-ag'):
        print('has agent')
        str_data = str(data)
        ins_index = str(data).index('-ag')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")
        for e in name:
            ee = e.strip()
            # print(ee)
            for ins in f_data:
                if ee == ins['pos']:
                    pid = ins['policyid']
                    qs_list.append(Policy.objects.filter(
                        policyid=pid).values())

        print('agent length: ', len(qs_list))

    if str_dataa.__contains__('-ins'):
        print('')
        print('has ins')
        str_data = str(data)
        ins_index = str(data).index('-ins')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['insurance_company']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['insurance_company']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('ins length: ', len(qs_list))

    if str_dataa.__contains__('-vc'):
        print('')
        print('has vc')
        str_data = str(data)
        ins_index = str(data).index('-vc')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['vehicle_catagory']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['vehicle_catagory']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('vc length: ', len(qs_list))

    if str_dataa.__contains__('-vmb'):
        print('')
        print('has vmb')
        str_data = str(data)
        ins_index = str(data).index('-vmb')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee.__contains__("--"):
                        ee = ee.replace("--", "/")

                    if ee == ins['vehicle_makeby']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                if ee.__contains__("--"):
                    ee = ee.replace("--", "/")
                # print(ee)

                for ins in f_data:
                    # inns = ins['vehicle_makeby']
                    # print('insss:' , inns)

                    if ee == ins['vehicle_makeby']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('vmb length: ', len(qs_list))

    if str_dataa.__contains__('-vmm'):
        print('')
        print('has vmm')
        str_data = str(data)
        ins_index = str(data).index('-vmm')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                if ee.__contains__("--"):
                    ee = ee.replace("--", "/")

                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['vehicle_model']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                if ee.__contains__("--"):
                    ee = ee.replace("--", "/")
                print(ee)

                for ins in f_data:
                    if ee == ins['vehicle_model']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('vm length: ', len(qs_list))

    if str_dataa.__contains__('-ft'):
        print('')
        print('has ft')
        str_data = str(data)
        ins_index = str(data).index('-ft')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['vehicle_fuel_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['vehicle_fuel_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('ft length: ', len(qs_list))

    if str_dataa.__contains__('-cc'):
        print('')
        print('has cc')
        str_data = str(data)
        ins_index = str(data).index('-cc')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['cubic_capacity']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['cubic_capacity']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('cc length: ', len(qs_list))

    if str_dataa.__contains__('-sc'):
        print('')
        print('has sc')
        str_data = str(data)
        ins_index = str(data).index('-sc')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['seating_capacity']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['seating_capacity']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('sc length: ', len(qs_list))

    if str_dataa.__contains__('-ct'):
        print('')
        print('has ct')
        str_data = str(data)
        ins_index = str(data).index('-ct')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['coverage_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['coverage_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('ct length: ', len(qs_list))

    if str_dataa.__contains__('-gvw'):
        print('')
        print('has gvw')
        str_data = str(data)
        ins_index = str(data).index('-gvw')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['gvw']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['gvw']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('gvw length: ', len(qs_list))

    if str_dataa.__contains__('-pt'):
        print('')
        print('has pt')
        str_data = str(data)
        ins_index = str(data).index('-pt')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['policy_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['policy_type']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('pt length: ', len(qs_list))

    if str_dataa.__contains__('-addon'):
        print('')
        print('has addon')
        str_data = str(data)
        ins_index = str(data).index('-addon')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['addon']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['addon']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('addon length: ', len(qs_list))

    if str_dataa.__contains__('-ncb'):
        print('')
        print('has ncb')
        str_data = str(data)
        ins_index = str(data).index('-ncb')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['ncb']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['ncb']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('ncb length: ', len(qs_list))

    if str_dataa.__contains__('-cpa'):
        print('')
        print('has cpa')
        str_data = str(data)
        ins_index = str(data).index('-cpa')
        # print('num', ins_index)

        b_index = str_data.index('[', ins_index)
        c_index = str_data.index(']', ins_index)

        subStr = str_data[b_index:c_index]
        # print(subStr)

        name = subStr.strip().replace(
            '[', '').replace(']', '').replace("'", '').split(",")

        if len(qs_list) > 0:
            qs_list_temp = list(chain(*qs_list))
            qs_list = []

            for e in name:
                ee = e.strip()
                print(ee)

                for ins in qs_list_temp:
                    if ee == ins['cpa']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())
        else:
            for e in name:
                ee = e.strip()
                print(ee)

                for ins in f_data:
                    if ee == ins['cpa']:
                        pid = ins['policyid']
                        qs_list.append(Policy.objects.filter(
                            policyid=pid).values())

        print('cpa length: ', len(qs_list))

    # print('qs list ', qs_list)

    print('qs list length', len(qs_list))
    return qs_list


def policy_entrydata(request, id):
    print('policy_entrydata')

    if request.method == "POST":

        proposal_no = request.POST['proposal_no']
        policy_no = request.POST['policy_no']
        customer_name = request.POST['customer_name']
        insurance_company = request.POST['insurance_company']
        sp_name = request.POST['sp_name']
        sp_brokercode = request.POST['sp_brokercode']

        try:
            product_name = request.POST['product_name']
        except:
            product_name = ''
        try:
            registration_no = request.POST['registration_no']
        except:
            registration_no = ''
        try:
            rto_city = request.POST['rto_city']
        except:
            rto_city = ''
        try:
            rto_state = request.POST['rto_state']
        except:
            rto_state = ''
        try:
            vehicle_makeby = request.POST['vehicle_makeby']
        except:
            vehicle_makeby = ''
        try:
            vehicle_model = request.POST['vehicle_model']
        except:
            vehicle_model = ''
        try:
            vehicle_catagory = request.POST['vehicle_catagory']
        except:
            vehicle_catagory = ''
        try:
            vehicle_fuel_type = request.POST['vehicle_fuel_type']
        except:
            vehicle_fuel_type = ''
        try:
            mfg_year = request.POST['mfg_year']
        except:
            mfg_year = None
        try:
            addon = request.POST['addon']
        except:
            addon = ''
        try:
            ncb = request.POST['ncb']
        except:
            ncb = ''
        try:
            cubic_capacity = request.POST['cubic_capacity']
        except:
            cubic_capacity = ''
        try:
            gvw = request.POST['gvw']
        except:
            gvw = ''
        try:
            seating_capacity = request.POST['seating_capacity']
        except:
            seating_capacity = ''
        try:
            coverage_type = request.POST['coverage_type']
        except:
            coverage_type = ''

        policy_type = request.POST['policy_type']

        try:
            cpa = request.POST['cpa']
        except:
            cpa = ''
        # risk_start_date = request.POST['risk_start_date']
        # risk_end_date = request.POST['risk_end_date']
        # issue_date = request.POST['issue_date']
        try:
            insured_age = request.POST['insured_age']
        except:
            insured_age = 0

        policy_term = request.POST['policy_term']
        bqp = request.POST['bqp']
        pos = request.POST['pos']
        employee = get_id_from_session(request)  # request.POST['employee']

        try:
            remark = request.POST['remark']
        except:
            remark = ''

        OD_premium = request.POST['od']
        TP_terrorism = request.POST['tpt']
        net = request.POST['net']
        gst_amount = request.POST['gst']
        try:
            gst_gcv_amount = request.POST['gstt']
        except:
            gst_gcv_amount = 0

        total = request.POST['total']
        payment_mode = request.POST['payment_mode']

        proposal = request.FILES.get('proposal')
        mandate = request.FILES.get('mandate')
        policy = request.FILES.get('policy')
        previous_policy = request.FILES.get('previous_policy')
        pan_card = request.FILES.get('pan_card')
        aadhar_card = request.FILES.get('aadhar_card')
        vehicle_rc = request.FILES.get('vehicle_rc')
        inspection_report = request.FILES.get('inspection_report')

        data = Policy.objects.filter(policyid=id)

        print('sp_brokercode', sp_brokercode)
        print('cpa', cpa)
        data.update(proposal_no=proposal_no, policy_no=policy_no, product_name=product_name, customer_name=customer_name, insurance_company=insurance_company, sp_name=sp_name,
                    sp_brokercode=sp_brokercode,  registration_no=registration_no,
                    rto_state=rto_state, rto_city=rto_city,  vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model, vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type,
                    mfg_year=mfg_year,
                    addon=addon, ncb=ncb, cubic_capacity=cubic_capacity, gvw=gvw, seating_capacity=seating_capacity, coverage_type=coverage_type, policy_type=policy_type, cpa=cpa,

                    insured_age=insured_age,

                    policy_term=policy_term, payment_mode=payment_mode, bqp=bqp, pos=pos,
                    employee=employee,
                    OD_premium=OD_premium,  TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount,
                    gst_gcv_amount=gst_gcv_amount,  total=total, remark=remark)

        fspr = FileSystemStorage()
        fsm = FileSystemStorage()
        fsp = FileSystemStorage()
        fspp = FileSystemStorage()
        fspc = FileSystemStorage()
        fsac = FileSystemStorage()
        fsvc = FileSystemStorage()
        fsis = FileSystemStorage()
        if proposal is not None:
            fspr.save(proposal.name, proposal)
        if mandate is not None:
            fsm.save(mandate.name, mandate)
        if policy is not None:
            fsp.save(policy.name, policy)
        if previous_policy is not None:
            fspp.save(previous_policy.name, previous_policy)
        if pan_card is not None:
            fspc.save(pan_card.name, pan_card)
        if aadhar_card is not None:
            fsac.save(aadhar_card.name, aadhar_card)
        if vehicle_rc is not None:
            fsvc.save(vehicle_rc.name, vehicle_rc)
        if inspection_report is not None:
            fsis.save(inspection_report.name, inspection_report)

        if proposal:
            data.update(proposal=proposal)
        if mandate:
            data.update(mandate=mandate)

        if policy:
            data.update(policy=policy)
        if previous_policy:
            data.update(previous_policy=previous_policy)
        if pan_card:
            data.update(pan_card=pan_card)
        if aadhar_card:
            data.update(aadhar_card=aadhar_card)
        if vehicle_rc:
            data.update(vehicle_rc=vehicle_rc)
        if inspection_report:
            data.update(inspection_report=inspection_report)

        # data = Policy.objects.filter(profile_id=profile_id).order_by('-policyid').values()
        print('all data', data)
        return render(request, 'policylist/policy_entry_list.html', {'data': data})

        # return redirect('bima_policy:policy_entry')

    else:
        data = Policy.objects.get(policyid=id)

        print('data: ', data)

        # getting products name and sorts them.
        products = []
        for p in Product.objects.values('name'):
            products.append(p['name'])
        products.sort()

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values('full_name'):
            agents.append(ag['full_name'])
        agents.sort()

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting service_providers name
        service_providers = []
        for provider in ServiceProvider.objects.values('full_name'):
            service_providers.append(provider['full_name'])
        service_providers.sort()

        # getting office_codes
        broker_codes = []
        for code in BrokerCode.objects.values('code'):
            broker_codes.append(code['code'])
        broker_codes.sort()

        # getting bqps
        bqps = []
        for bqp in BQP.objects.values('name'):
            bqps.append(bqp['name'])
        bqps.sort()

        user_info = {
            "user_id": get_id_from_session(request),
            "user_name": get_user_name(request),
            "user_role": get_user_role(request)
        }

        vehicle_categories = ''
        makes = ''
        models = ''

        is_motor_form = True

        if data.registration_no is '':
            is_motor_form = False
            data.registration_no = ''
            data.rto_city = ''
            data.rto_state = ''
            data.vehicle_makeby = ''
            data.vehicle_model = ''
            data.vehicle_catagory = ''
            data.vehicle_fuel_type = ''
            data.mfg_year = ''
            data.addon = ''
            data.ncb = ''
            data.cubic_capacity = ''
            data.gvw = ''
            data.seating_capacity = ''
            data.coverage_type = ''

        if is_motor_form:
            # getting vehicle categories name and sort them.
            vehicle_categories = []
            for category in VehicleCategory.objects.values("category"):
                vehicle_categories.append(category['category'])
            vehicle_categories.sort()

            makes = VehicleMake.objects.values('make')
            models = VehicleModel.objects.values('model')

        context = {
            "data": data,
            "products": products,
            "agents": agents,
            "insurers": insurers,
            "service_providers": service_providers,
            "broker_codes": broker_codes,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models,
            "bqps": bqps,
            "is_user": is_user(request),
            "user_id": get_id_from_session(request),
            "user_name": get_user_name(request),
            "is_motor_form": is_motor_form
        }
        return render(request, 'policylist/edit_policy.html', context)


def edit_policy(request, id):
    print('edit policy method is calling')
    if request.method == "GET":
        data = Policy.objects.filter(policyid=id)
        datai = InsuranceCompany.objects.filter(
            profile_id=get_id_from_session(request))
        datasp = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))
        databc = BrokerCode.objects.filter(
            profile_id=get_id_from_session(request))
        datamb = VehicleMakeBy.objects.filter(
            profile_id=get_id_from_session(request))
        datavm = VehicleModelName.objects.filter(
            profile_id=get_id_from_session(request))
        datavc = VehicleCategory.objects.filter(
            profile_id=get_id_from_session(request))
        datag = Agents.objects.filter(
            profile_id=get_id_from_session(request), status="Active")
        return render(request, 'policylist/edit_policy.html', {'data': data, 'datasp': datasp, 'databc': databc, 'datamb': datamb, 'datavm': datavm, 'datavc': datavc, 'datag': datag, 'datai': datai})
    else:
        policy_no = request.POST['policy_no']
        registration = request.POST['registration']
        case_type = request.POST['case_type']
        ins_company = request.POST['ins_company']
        service_provider = request.POST['service_provider']
        code = request.POST['code']
        issue_date = request.POST['issue_date']
        risk_date = request.POST['risk_date']
        cpa = request.POST['cpa']
        document = request.FILES.get('document')
        fs = FileSystemStorage()
        fs.save(document.name, document)
        previous_policy = request.FILES.get('previous_policy')
        fs1 = FileSystemStorage()
        if previous_policy is not None:
            fs1.save(previous_policy.name, previous_policy)
        vehicle_rc = request.FILES.get('vehicle_rc')
        fs2 = FileSystemStorage()
        if vehicle_rc is not None:
            fs2.save(vehicle_rc.name, vehicle_rc)
        vehicle_makeby = request.POST['vehicle_makeby']
        vehicle_model = request.POST['vehicle_model']
        vehicle_category = request.POST['vehicle_category']
        vehicle_other_info = request.POST['vehicle_other_info']
        fuel_type = request.POST['fuel_type']
        manu_year = request.POST['manu_year']
        engine_no = request.POST['engine_no']
        chasis_no = request.POST['chasis_no']
        agent = request.POST['agent']
        cust_name = request.POST['cust_name']
        remarks = request.POST['remarks']
        od = request.POST['od']
        tp = request.POST['tp']
        gst = request.POST['gst']
        net = request.POST['total']
        payment_mode = request.POST['payment_mode']
        total = request.POST['total']
        policy_type = request.POST.get('policy_type')
        Policy.objects.filter(policyid=id).update(policy_no=policy_no, registration_no=registration, casetype=case_type, insurance_comp=ins_company, sp_name=service_provider, sp_brokercode=code, issueDate=issue_date, riskDate=risk_date, CPA=cpa, insurance=document, previous_policy=previous_policy, vehicle_rc=vehicle_rc, vehicle_makeby=vehicle_makeby,
                                                  vehicle_model=vehicle_model, vehicle_category=vehicle_category, other_info=vehicle_other_info, vehicle_fuel_type=fuel_type, manufature_year=manu_year, engine_no=engine_no, chasis_no=chasis_no, agent_name=agent, customer_name=cust_name, remark=remarks, OD_premium=od, TP_premium=tp, GST=gst, net=net, payment_mode=payment_mode, total=total, policy_type=policy_type)
        return redirect('bima_policy:policy_entry')


def policy_delete(request, id):
    print('policy_delete')

    if request.method == 'GET':
        try:
            print('id', id)
            if id.__contains__("|"):
                ids = id.split("|")
                for id in ids:
                    # pp = Policy.objects.filter(policyid=id).delete()
                    pass
            else:
                print('deleting single policy:')
                values_list = Policy.objects.filter(policyid=id).values()

                for i in values_list:
                    print(i)

                proposal_no = values_list[0]['proposal_no']
                policy_no = values_list[0]['policy_no']
                customer_name = values_list[0]['customer_name']
                insurance_company = values_list[0]['insurance_company']
                sp_name = values_list[0]['sp_name']
                sp_brokercode = values_list[0]['sp_brokercode']
                registration_no = values_list[0]['registration_no']
                rto_state = values_list[0]['rto_state']
                rto_city = values_list[0]['rto_city']
                vehicle_makeby = values_list[0]['vehicle_makeby']
                vehicle_model = values_list[0]['vehicle_model']
                vehicle_catagory = values_list[0]['vehicle_catagory']
                vehicle_fuel_type = values_list[0]['vehicle_fuel_type']
                mfg_year = values_list[0]['mfg_year']
                addon = values_list[0]['addon']
                ncb = values_list[0]['ncb']
                try:
                    cubic_capacity = values_list[0]['cubic_capacity']
                except Exception as ex:
                    cubic_capacity = ''
                gvw = values_list[0]['gvw']
                seating_capacity = values_list[0]['seating_capacity']
                coverage_type = values_list[0]['coverage_type']
                policy_type = values_list[0]['policy_type']
                cpa = values_list[0]['cpa']
                risk_start_date = values_list[0]['risk_start_date']
                risk_end_date = values_list[0]['risk_end_date']
                issue_date = values_list[0]['issue_date']
                insured_age = values_list[0]['insured_age']
                policy_term = values_list[0]['policy_term']
                bqp = values_list[0]['bqp']
                pos = values_list[0]['pos']

                employee = values_list[0]['employee']

                try:
                    remark = values_list[0]['remark']
                except Exception as ex:
                    remark = ''

                OD_premium = values_list[0]['od']
                TP_terrorism = values_list[0]['tpt']
                net = values_list[0]['net']
                gst_amount = values_list[0]['gst']
                try:
                    gst_gcv_amount = values_list[0]['gstt']
                except Exception as ex:
                    gst_gcv_amount = 0

                total = values_list[0]['total']
                payment_mode = values_list[0]['payment_mode']

                # proposal = ""
                # mandate = ''
                # policy = ''
                # previous_policy = ''
                # pan_card = ''
                # aadhar_card = ''
                # vehicle_rc = ''
                # inspection_report = ''

                try:

                    pol = DeletedPolicy.objects.create(remark="Manjeet Nandal")
                    print('pol is: ', pol)

                except Exception as esd:
                    print(str(esd))

                # Policy.objects.get(policyid=id).delete()

        except Exception as ex:
            print(ex)
        return redirect('bima_policy:policy_entry')


def logout(request):
    request.session.clear()
    return render(request, 'login.html')


def agent(request):
    print('agent method')
    return render(request, 'agents/agent.html')

    # data = Agents.objects.filter(profile_id=get_id_from_session(request))
    data = Agents.objects.filter(status="Active")

    print(data)
    return render(request, 'agents/agent.html', {'data': data})


def add_agent(request):
    try:
        if request.method == "GET":
            Adata = Slab.objects.all()
            return render(request, 'agents/add_agent.html', {'Adata': Adata})
    except Agents.DoesNotExist:
        return render(request, 'agents/add_agent.html')
    else:
        if 'subagent' in request.POST:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            posp_code = request.POST['posp_code']
            registration_code = request.POST['registration_code']
            full_name = request.POST['full_name']
            gender = request.POST['gender']
            mob_no = request.POST['mob_no']
            email_id = request.POST['email_id']
            address = request.POST['address']
            state = request.POST['state']
            city = request.POST['city']
            pincode = request.POST['pincode']
            rural_urban = request.POST['rural_urban']
            slab = request.POST['slab']
            GSTIN = request.POST['GSTIN']
            account_no = request.POST['account_no']
            ifsc_code = request.POST['ifsc_code']
            bank_name = request.POST['bank_name']

            basic_qualification = request.FILES.get('basic_qualification')
            aadhar_card = request.FILES.get('aadhar_card')
            pan_card = request.FILES.get('pan_card')
            training_certificate = request.FILES.get('training_certificate')
            appointment_certificate = request.FILES.get(
                'appointment_certificate')
            agreement_certificate = request.FILES.get('agreement_certificate')
            bank_details = request.FILES.get('bank_details')

            fsp = FileSystemStorage()
            if basic_qualification is not None:
                fsp.save(basic_qualification.name, basic_qualification)
            if aadhar_card is not None:
                fsp.save(aadhar_card.name, aadhar_card)
            if pan_card is not None:
                fsp.save(pan_card.name, pan_card)
            if training_certificate is not None:
                fsp.save(training_certificate.name, training_certificate)
            if appointment_certificate is not None:
                fsp.save(appointment_certificate.name, appointment_certificate)
            if agreement_certificate is not None:
                fsp.save(agreement_certificate.name, agreement_certificate)
            if bank_details is not None:
                fsp.save(bank_details.name, bank_details)

            password = request.POST['password']
            # otp = random.randint(1000, 9999)
            # print('under otp: ', otp)
            created_by = get_id_from_session(request)

            data = Agents.objects.create(posp_code=posp_code,
                                         registration_code=registration_code,
                                         full_name=full_name, gender=gender,
                                         mob_no=mob_no,
                                         email_id=email_id,
                                         address=address,
                                         state=state,
                                         city=city,
                                         pincode=pincode,
                                         rural_urban=rural_urban,
                                         slab=slab,
                                         GSTIN=GSTIN,
                                         account_no=account_no,
                                         ifsc_code=ifsc_code,
                                         bank_name=bank_name,
                                         basic_qualification=basic_qualification,
                                         aadhar_card=aadhar_card,
                                         pan_card=pan_card,
                                         training_certificate=training_certificate,
                                         appointment_certificate=appointment_certificate,
                                         agreement_certificate=agreement_certificate,
                                         bank_details=bank_details,
                                         password=password,
                                         #  otp=otp,
                                         created_by=created_by,
                                         profile_id=data)

            print('data is ', data.login_id)
            print('data status ', data.status)

            return redirect('bima_policy:agent')

            if send_otp(otp) == "":
                print('sent')
                return redirect('bima_policy:verify_agent', data.login_id)
            else:
                print('failed')
                return HttpResponse('Error occurred')

            # return redirect('bima_policy:agent')


def edit_agent(request, id):
    print('\nedit agent calling:')

    try:
        if request.method == "GET":
            data = Agents.objects.filter(login_id=id).first()
            return render(request, 'agents/edit_agent.html', {'data': data})

        elif request.method == "POST":
            # data = ProfileModel.objects.get(id=get_id_from_session(request))
            posp_code = request.POST['posp_code']
            registration_code = request.POST['registration_code']
            full_name = request.POST['full_name']
            gender = request.POST['gender']
            mob_no = request.POST['mob_no']
            email_id = request.POST['email_id']
            address = request.POST['address']
            state = request.POST['state']
            city = request.POST['city']
            pincode = request.POST['pincode']
            rural_urban = request.POST['rural_urban']
            slab = request.POST['slab']
            GSTIN = request.POST['GSTIN']
            account_no = request.POST['account_no']
            ifsc_code = request.POST['ifsc_code']
            bank_name = request.POST['bank_name']

            created_by = get_id_from_session(request)

            data = Agents.objects.filter(login_id=id)

            data.update(posp_code=posp_code,
                        registration_code=registration_code,
                        full_name=full_name, gender=gender,
                        mob_no=mob_no,
                        email_id=email_id,
                        address=address,
                        state=state,
                        city=city,
                        pincode=pincode,
                        rural_urban=rural_urban,
                        slab=slab,
                        GSTIN=GSTIN,
                        account_no=account_no,
                        ifsc_code=ifsc_code,
                        bank_name=bank_name,
                        created_by=created_by)

            basic_qualification = request.FILES.get('basic_qualification')
            aadhar_card = request.FILES.get('aadhar_card')
            pan_card = request.FILES.get('pan_card')
            training_certificate = request.FILES.get('training_certificate')
            appointment_certificate = request.FILES.get(
                'appointment_certificate')
            agreement_certificate = request.FILES.get('agreement_certificate')
            bank_details = request.FILES.get('bank_details')

            fsp = FileSystemStorage()
            if basic_qualification is not None:
                fsp.save(basic_qualification.name, basic_qualification)
                data.update(basic_qualification=basic_qualification.name)

            if aadhar_card is not None:
                fsp.save(aadhar_card.name, aadhar_card)
                data.update(aadhar_card=aadhar_card.name)

            if pan_card is not None:
                fsp.save(pan_card.name, pan_card)
                data.update(pan_card=pan_card.name)

            if training_certificate is not None:
                fsp.save(training_certificate.name, training_certificate)
                data.update(training_certificate=training_certificate.name)

            if appointment_certificate is not None:
                fsp.save(appointment_certificate.name, appointment_certificate)
                data.update(
                    appointment_certificate=appointment_certificate.name)

            if agreement_certificate is not None:
                fsp.save(agreement_certificate.name, agreement_certificate)
                data.update(agreement_certificate=agreement_certificate.name)

            if bank_details is not None:
                fsp.save(bank_details.name, bank_details)
                data.update(bank_details=bank_details.name)

            print('agent updated\n')
            return redirect('bima_policy:agent')

    except Exception as e:
        print(str(e))
        return HttpResponse(str(e))


def delete_agent(request, id):
    print('\ndelete agent calling:')
    # print(id)
    try:
        Agents.objects.filter(login_id=id).delete()
        print('agent deleted\n')
        return redirect('bima_policy:agent')
    except Exception as e:
        print(str(e))
        return HttpResponse(str(e))


def verify_agent(request, id):
    print('verify_agent calling: ', id)
    try:
        if request.method == "GET":
            return render(request, 'agents/otp_verification.html')

        elif request.method == "POST":
            data = Agents.objects.filter(login_id=id, status="")
            otp = request.POST['otp']
            if otp == data[0].otp:
                index = data.update(status="Active")
                if index == 1:
                    return redirect('bima_policy:agent')
                else:
                    return HttpResponse('No Status of: ', + data[0].full_name)
            else:
                print('OTP didnt Matched')
                return HttpResponse('OTP didnt Matched of: ' + data[0].full_name)

    except Agents.DoesNotExist:
        return render(request, 'agents/add_agent.html')

# PayoutView


def slab(request):
    if request.method == "GET":
        try:
            # data = Slab.objects.filter(profile_id=get_id_from_session(request))
            data = Slab.objects.all()
            return render(request, 'payout/slab.html', {'data': data})
        except Slab.DoesNotExist:
            return render(request, 'payout/slab.html')
    else:
        try:
            if 'slab_add' in request.POST:
                profile = ProfileModel.objects.get(
                    id=get_id_from_session(request))
                slab_name = request.POST['slab']
                Slab.objects.create(slab_name=slab_name, profile_id=profile)
                return redirect('bima_policy:slab')
            # if 'slab_remove' in request.POST:

        except ProfileModel.DoesNotExist:
            return redirect('bima_policy:slab')


def slab_delete(request, id):
    data = Slab.objects.filter(slab_name=id)
    data.delete()
    return redirect('bima_policy:slab')


def slab_copy(request, id):
    print('slab copy method')
    try:
        data = Slab.objects.filter(slab_name=id).values()

        slab_name = data[0]['slab_name'] + \
            '_copy_' + uuid.uuid4().hex[:3].upper()

        new_slab = Slab.objects.create(
            profile_id_id=data[0]['profile_id_id'], slab_name=slab_name)

        temp = Payout.objects.filter(slab_name=data[0]['slab_name']).values()

        for i in temp:
            print(i['payoutid'])
            payout_copy_all(request, i['payoutid'], new_slab)
    except:
        return HttpResponse('Error occurred in slab_copy')

    return redirect('bima_policy:slab')


def payout_copy_all(request, id, slab):
    data = ProfileModel.objects.get(id=get_id_from_session(request))
    temp = Payout.objects.filter(payoutid=id).values()
    payout_name = temp[0]['payout_name'] + \
        '_copy_' + uuid.uuid4().hex[:3].upper()
    s = slab
    product_name = temp[0]['product_name']
    insurance_company = temp[0]['insurance_company']
    sp_name = temp[0]['sp_name']
    sp_brokercode = temp[0]['sp_brokercode']
    vehicle_makeby = temp[0]['vehicle_makeby']
    vehicle_model = temp[0]['vehicle_model']
    vehicle_catagory = temp[0]['vehicle_catagory']
    vehicle_fuel_type = temp[0]['vehicle_fuel_type']
    mfg_year = temp[0]['mfg_year']
    addon = temp[0]['addon']
    ncb = temp[0]['ncb']
    gvw = temp[0]['gvw']
    cubic_capacity = temp[0]['cubic_capacity']
    seating_capacity = temp[0]['seating_capacity']
    coverage_type = temp[0]['coverage_type']
    policy_type = temp[0]['policy_type']
    policy_term = temp[0]['policy_term']
    cpa = temp[0]['cpa']
    rto = temp[0]['rto_city']

    # agent payout
    agent_od_reward = temp[0]['agent_od_reward']
    agent_tp_reward = temp[0]['agent_tp_reward']
    # self payout
    self_od_reward = temp[0]['self_od_reward']
    self_tp_reward = temp[0]['self_tp_reward']

    data = Payout.objects.create(payout_name=payout_name, slab_name=s, product_name=product_name,
                                 insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                                 vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model,
                                 vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type, mfg_year=mfg_year,
                                 rto_city=rto, addon=addon, ncb=ncb, gvw=gvw, cubic_capacity=cubic_capacity, seating_capacity=seating_capacity,
                                 coverage_type=coverage_type, policy_type=policy_type, cpa=cpa, policy_term=policy_term,
                                 agent_od_reward=agent_od_reward,
                                 agent_tp_reward=agent_tp_reward,
                                 self_od_reward=self_od_reward,
                                 self_tp_reward=self_tp_reward,
                                 profile_id=data)
    print("insert data")
    print(data)
    return 'done'

    try:
        pdata = Payout.objects.filter(
            profile_id=get_id_from_session(request))

        return render(request, 'payout/slab_payoutlist.html', {'data1': pdata})
    except Payout.DoesNotExist:
        return render(request, 'payout/slab_payoutlist.html')


def slab_edit(request, id):
    data = Slab.objects.filter(slab_name=id)
    if request.method == 'GET':
        return render(request, 'payout/payoutname_edit.html', {'data': data})
    else:
        slab_name = request.POST['slab_name']
        status = request.POST['status']
        Slab.objects.filter(slab_name=id).update(
            slab_name=slab_name, status=status)
        return redirect('bima_policy:slab')


def slab_payout(request, id):
    print('slab_payout calling:')
    if request.method == 'GET':
        try:
            data = Payout.objects.filter(
                profile_id=get_id_from_session(request))
            # data = Payout.objects.all()
            data1 = data.filter(slab_name=id)
            return render(request, 'payout/slab_payoutlist.html', {'data1': data1})
        except Payout.DoesNotExist:
            return render(request, 'payout/slab_payoutlist.html')


def slab_payoutform(request):
    print('slab_payoutform')

    if request.method == "GET":
        print('slab_payoutform get')

        slab = Slab.objects.values()

        # getting products name and sorts them.
        products = []
        for p in Product.objects.values('name'):
            products.append(p['name'])
        products.sort()

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values('full_name'):
            agents.append(ag['full_name'])
        agents.sort()

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting service_providers name
        service_providers = []
        for provider in ServiceProvider.objects.values('full_name'):
            service_providers.append(provider['full_name'])
        service_providers.sort()

        # getting office_codes
        broker_codes = []
        for code in BrokerCode.objects.values('code'):
            broker_codes.append(code['code'])
        broker_codes.sort()

        # getting vehicle categories name and sort them.
        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = VehicleMake.objects.values('make')
        models = VehicleModel.objects.values('model')

        context = {
            "slab": slab,
            "products": products,
            "agents": agents,
            "insurers": insurers,
            "service_providers": service_providers,
            "broker_codes": broker_codes,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models
        }

        return render(request, 'payout/slab_payoutform.html', context)

    if request.method == 'POST' and 'savepayout' in request.POST:
        print("data enter")
        data = ProfileModel.objects.get(id=get_id_from_session(request))
        payout_name = request.POST['payout_name']
        slab = request.POST['slab']
        s = Slab.objects.get(slab_name=slab)
        product_name = request.POST.getlist('product_name')
        insurance_company = request.POST.getlist('insurer')
        sp_name = request.POST.getlist('sp_name')
        sp_brokercode = request.POST.getlist('sp_brokercode')
        vehicle_makeby = request.POST.getlist('vehicle_makeby')
        vehicle_model = request.POST.getlist('vehicle_model')
        vehicle_catagory = request.POST.getlist('vehicle_catagory')
        vehicle_fuel_type = request.POST.getlist('vehicle_fuel_type')
        mfg_year = request.POST.getlist('mfg_year')
        addon = request.POST.getlist('addon')
        ncb = request.POST.getlist('ncb')
        gvw = request.POST.getlist('gvw')
        cubic_capacity = request.POST.getlist('cubic_capacity')
        seating_capacity = request.POST.getlist('seating_capacity')
        coverage_type = request.POST.getlist('coverage_type')
        policy_type = request.POST.getlist('policy_type')
        policy_term = request.POST.getlist('policy_term')
        cpa = request.POST.getlist('cpa')
        rto = request.POST.getlist('rto')

        # agent payout
        agent_od_reward = request.POST['agent_od_reward']
        agent_tp_reward = request.POST['agent_tp_reward']
        # self payout
        self_od_reward = request.POST['self_od_reward']
        self_tp_reward = request.POST['self_tp_reward']

        vehicle_makeby = str(vehicle_makeby).replace('\\r\\n', '')
        vehicle_model = str(vehicle_model).replace('\\r\\n', '')
        vehicle_makeby = str(vehicle_makeby).replace(
            "['", '').replace("']", '').replace("'", '')
        vehicle_model = str(vehicle_model).replace(
            "['", '').replace("']", '').replace("'", '')

        rto = str(rto).replace("['", '').replace("']", '').replace("'", '')

        product_name = ', '.join(product_name)
        insurance_company = ', '.join(insurance_company)
        sp_name = ', '.join(sp_name)
        sp_brokercode = ', '.join(sp_brokercode)
        # vehicle_makeby = ', '.join(vehicle_makeby)
        # vehicle_model = ', '.join(vehicle_model)
        vehicle_catagory = ', '.join(vehicle_catagory)
        vehicle_fuel_type = ', '.join(vehicle_fuel_type)
        mfg_year = ', '.join(mfg_year)
        rto_city = ', '.join(rto)
        addon = ', '.join(addon)
        ncb = ', '.join(ncb)
        gvw = ', '.join(gvw)
        cubic_capacity = ', '.join(cubic_capacity)
        seating_capacity = ', '.join(seating_capacity)
        coverage_type = ', '.join(coverage_type)
        policy_type = ', '.join(policy_type)
        cpa = ', '.join(cpa)
        policy_term = ', '.join(policy_term)

        # my_list = product_names.split(",")
        # print( my_list)

        data = Payout.objects.create(payout_name=payout_name, slab_name=s, product_name=product_name,
                                     insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                                     vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model,
                                     vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type, mfg_year=mfg_year,
                                     rto_city=rto, addon=addon, ncb=ncb, gvw=gvw, cubic_capacity=cubic_capacity, seating_capacity=seating_capacity,
                                     coverage_type=coverage_type, policy_type=policy_type, cpa=cpa, policy_term=policy_term,
                                     agent_od_reward=agent_od_reward,
                                     agent_tp_reward=agent_tp_reward,
                                     self_od_reward=self_od_reward,
                                     self_tp_reward=self_tp_reward,
                                     profile_id=data)

        return redirect('bima_policy:slab')


def slab_payoutformshow(request, id):
    print('slab_payoutformshow')
    if request.method == "POST":
        payout_name = request.POST['payout_name']
        product_name = request.POST.getlist('product_name')
        insurance_company = request.POST.getlist('insurer')
        sp_name = request.POST.getlist('sp_name')
        sp_brokercode = request.POST.getlist('sp_brokercode')
        vehicle_makeby = request.POST.getlist('vehicle_makeby')
        vehicle_model = request.POST.getlist('vehicle_model')
        vehicle_catagory = request.POST.getlist('vehicle_catagory')
        vehicle_fuel_type = request.POST.getlist('vehicle_fuel_type')
        mfg_year = request.POST.getlist('mfg_year')
        addon = request.POST.getlist('addon')
        ncb = request.POST.getlist('ncb')
        gvw = request.POST.getlist('gvw')
        cubic_capacity = request.POST.getlist('cubic_capacity')
        seating_capacity = request.POST.getlist('seating_capacity')
        coverage_type = request.POST.getlist('coverage_type')
        policy_type = request.POST.getlist('policy_type')
        policy_term = request.POST.getlist('policy_term')
        cpa = request.POST.getlist('cpa')
        rto = request.POST.getlist('rto')

        # agent payout
        agent_od_reward = request.POST['agent_od_reward']
        agent_tp_reward = request.POST['agent_tp_reward']
        # self payout
        self_od_reward = request.POST['self_od_reward']
        self_tp_reward = request.POST['self_tp_reward']

        vehicle_makeby = str(vehicle_makeby).replace('\\r\\n', '')
        vehicle_model = str(vehicle_model).replace('\\r\\n', '')
        vehicle_makeby = str(vehicle_makeby).replace(
            "['", '').replace("']", '').replace("'", '')
        vehicle_model = str(vehicle_model).replace(
            "['", '').replace("']", '').replace("'", '')

        rto_city = str(rto).replace(
            "['", '').replace("']", '').replace("'", '')

        product_name = ','.join(product_name)
        insurance_company = ','.join(insurance_company)
        sp_name = ','.join(sp_name)
        sp_brokercode = ','.join(sp_brokercode)
        # vehicle_makeby = ','.join(vehicle_makeby)
        # vehicle_model = ','.join(vehicle_model)
        vehicle_catagory = ','.join(vehicle_catagory)
        vehicle_fuel_type = ','.join(vehicle_fuel_type)
        mfg_year = ','.join(mfg_year)
        # rto_city = ','.join(rto)
        addon = ','.join(addon)
        ncb = ','.join(ncb)
        gvw = ','.join(gvw)
        cubic_capacity = ','.join(cubic_capacity)
        seating_capacity = ','.join(seating_capacity)
        coverage_type = ','.join(coverage_type)
        policy_type = ','.join(policy_type)
        cpa = ','.join(cpa)
        policy_term = ','.join(policy_term)

        print(mfg_year)
        payout_updt = Payout.objects.filter(payoutid=id)
        # print("this is output", payout_updt.values())
        payout_updt.update(payout_name=payout_name,  product_name=product_name,
                           insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                           vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model,
                           vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type, mfg_year=mfg_year,
                           rto_city=rto_city, addon=addon, ncb=ncb, gvw=gvw, cubic_capacity=cubic_capacity, seating_capacity=seating_capacity,
                           coverage_type=coverage_type, policy_type=policy_type, cpa=cpa, policy_term=policy_term,
                           agent_od_reward=agent_od_reward,
                           agent_tp_reward=agent_tp_reward,
                           self_od_reward=self_od_reward,
                           self_tp_reward=self_tp_reward)
        try:
            data1 = Payout.objects.filter(
                profile_id=get_id_from_session(request))
            return render(request, 'payout/slab_payoutlist.html', {'data1': data1})
        except Payout.DoesNotExist:
            return render(request, 'payout/slab_payoutlist.html')

    else:
        slab = Slab.objects.filter(profile_id=get_id_from_session(request))

        data = Payout.objects.get(payoutid=id)

        # getting products name and sorts them.
        products = []
        for p in Product.objects.values('name'):
            products.append(p['name'])
        products.sort()

        # getting agents full name and sorts them.
        agents = []
        for ag in Agents.objects.filter(status="Active").values('full_name'):
            agents.append(ag['full_name'])
        agents.sort()

        # getting insurers name and sorts them.
        insurers = []
        for ins in InsuranceCompany.objects.values('comp_name'):
            insurers.append(ins['comp_name'])
        insurers.sort()

        # getting service_providers name
        service_providers = []
        for provider in ServiceProvider.objects.values('full_name'):
            service_providers.append(provider['full_name'])
        service_providers.sort()

        # getting office_codes
        broker_codes = []
        for code in BrokerCode.objects.values('code'):
            broker_codes.append(code['code'])
        broker_codes.sort()

        # getting vehicle categories name and sort them.
        vehicle_categories = []
        for category in VehicleCategory.objects.values("category"):
            vehicle_categories.append(category['category'])
        vehicle_categories.sort()

        makes = VehicleMake.objects.values('make')
        models = VehicleModel.objects.values('model')

        context = {
            "slab": slab,
            "products": products,
            "data": data,
            "agents": agents,
            "insurers": insurers,
            "service_providers": service_providers,
            "broker_codes": broker_codes,
            "vehicle_categories": vehicle_categories,
            "makes": makes,
            "models": models
        }

        # print(data.vehicle_makeby)
        return render(request, 'payout/edit_payoutform.html', context)


def payout_delete(request, id):
    Payout.objects.filter(payoutid=id).delete()
    return redirect('bima_policy:slab')


def payout_copy(request, id):
    data = ProfileModel.objects.get(id=get_id_from_session(request))
    temp = Payout.objects.filter(payoutid=id).values()
    payout_name = temp[0]['payout_name'] + '_copy'
    slab_name = temp[0]['slab_name_id']
    s = Slab.objects.get(slab_name=slab_name)
    product_name = temp[0]['product_name']
    insurance_company = temp[0]['insurance_company']
    sp_name = temp[0]['sp_name']
    sp_brokercode = temp[0]['sp_brokercode']
    vehicle_makeby = temp[0]['vehicle_makeby']
    vehicle_model = temp[0]['vehicle_model']
    vehicle_catagory = temp[0]['vehicle_catagory']
    vehicle_fuel_type = temp[0]['vehicle_fuel_type']
    mfg_year = temp[0]['mfg_year']
    addon = temp[0]['addon']
    ncb = temp[0]['ncb']
    gvw = temp[0]['gvw']
    cubic_capacity = temp[0]['cubic_capacity']
    seating_capacity = temp[0]['seating_capacity']
    coverage_type = temp[0]['coverage_type']
    policy_type = temp[0]['policy_type']
    policy_term = temp[0]['policy_term']
    cpa = temp[0]['cpa']
    rto = temp[0]['rto_city']

    # agent payout
    agent_od_reward = temp[0]['agent_od_reward']
    agent_tp_reward = temp[0]['agent_tp_reward']
    # self payout
    self_od_reward = temp[0]['self_od_reward']
    self_tp_reward = temp[0]['self_tp_reward']

    data = Payout.objects.create(payout_name=payout_name, slab_name=s, product_name=product_name,
                                 insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                                 vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model,
                                 vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type, mfg_year=mfg_year,
                                 rto_city=rto, addon=addon, ncb=ncb, gvw=gvw, cubic_capacity=cubic_capacity, seating_capacity=seating_capacity,
                                 coverage_type=coverage_type, policy_type=policy_type, cpa=cpa, policy_term=policy_term,
                                 agent_od_reward=agent_od_reward,
                                 agent_tp_reward=agent_tp_reward,
                                 self_od_reward=self_od_reward,
                                 self_tp_reward=self_tp_reward,
                                 profile_id=data)
    print("insert data")
    print(data)

    try:
        pdata = Payout.objects.filter(
            profile_id=get_id_from_session(request))

        return render(request, 'payout/slab_payoutlist.html', {'data1': pdata})
    except Payout.DoesNotExist:
        return render(request, 'payout/slab_payoutlist.html')


def payout_edit(request, id):
    data = Payout.objects.filter(payoutid=id)
    if request.method == "GET":
        pol_provider = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))
        ins_comp = InsuranceCompany.objects.filter(
            profile_id=get_id_from_session(request))
        vcat = VehicleCategory.objects.filter(
            profile_id=get_id_from_session(request))
        vmb = VehicleMakeBy.objects.filter(
            profile_id=get_id_from_session(request))
        vmodel = VehicleModelName.objects.filter(
            profile_id=get_id_from_session(request))
        slab = Slab.objects.filter(profile_id=get_id_from_session(request))
        return render(request, 'payout/edit_payoutform.html', {'slab': slab, 'vcat': vcat, 'vmb': vmb, 'vmodel': vmodel, 'ins_comp': ins_comp, 'pol_provider': pol_provider, 'data': data})

    if request.method == 'POST':
        payoutName = request.POST['payout_name']
        slab = request.POST['slab']
        s = Slab.objects.get(slab_name=slab)
        status = request.POST['status']
        if request.POST['vehicle_category'] == 'any':
            vehicle = list(VehicleCategory.objects.filter(
                profile_id=get_id_from_session(request)))
            vehicle_category = vehicle
            print(vehicle_category)
        else:
            vehicle_category = request.POST['vehicle_category']
        if request.POST['ins_com'] == 'any':
            ins = list(InsuranceCompany.objects.filter(
                profile_id=get_id_from_session(request)))
            Insurance_company = ins
            print(Insurance_company)
        else:
            Insurance_company = request.POST['ins_com']
        if request.POST['policy_provider'] == 'any':
            policy = list(ServiceProvider.objects.filter(
                profile_id=get_id_from_session(request)))
            policy_provider = policy
            print(policy_provider)
        else:
            policy_provider = request.POST['policy_provider']
        if request.POST['vehicle_category'] == 'any':
            vehiclemb = list(VehicleMakeBy.objects.filter(
                profile_id=get_id_from_session(request)))
            vehicle_make_by = vehiclemb
            print(vehicle_make_by)
        else:
            vehicle_make_by = request.POST['vehicle_make_by']
        rtos = request.POST['rtos']
        casetype = request.POST['casetype']
        coverage = request.POST['coverage']
        fueltype = request.POST['fueltype']
        cpa = request.POST['cpa']
        rewards_on = request.POST['areward_on']
        rewards_age = request.POST['areward_pct']
        self_rewards_on = request.POST['sreward_on']
        self_rewards_age = request.POST['sreward_pct']
        Payout.objects.filter(payoutid=id).update(payout_name=payoutName, slab_name=s, status=status, vehicle_category=vehicle_category, Insurance_company=Insurance_company, policy_provider=policy_provider, vehicle_make_by=vehicle_make_by,
                                                  rto=rtos.upper(), case_type=casetype, coverage=coverage, fuel_type=fueltype, cpa=cpa, rewards_on=rewards_on, rewards_age=rewards_age, self_rewards_on=self_rewards_on, self_rewards_age=self_rewards_age)
        return redirect('bima_policy:slab_payout')


def policy_import(request):
    if request.method == 'GET':
        return render(request, 'policylist/policy_list_import.html')
    else:
        if 'submitup' in request.POST:
            fcsv = request.FILES.get('fcsv')
            fs = FileSystemStorage()
            fs.save(fcsv.name, fcsv)
            InsuranceUpload.objects.create(ins_upload=fcsv)
            messages.success(request, 'Insurance upload succefully......')
            return HttpResponseRedirect(request.path, ('policylist/policy_list_import'))

# def apply_payout(request):
#     if request.method=='POST':
#         case_type=request.POST.get('case_type')
#         registration=request.POST.get('registration')
#         registration=registration[:4]
#         cpa=request.POST.get('cpa')
#         fuel_type=request.POST.get('fuel_type')
#         agent=request.POST.get('agent')
#         od=request.POST.get('od')
#         tp=request.POST.get('tp')
#         gst=request.POST.get('gst')
#         # print(registration)


def upcoming_renewal(request):
    return render(request, 'upcomingrenewal/upcoming_renewal.html')


def agentpayable(request):
    agent_obj = Agents.objects.filter(status="Active")
    policy_data = []
    grand_total_policy = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(agent_name=agent_name)
        total_policy = 0
        issueDate = ""
        for policy in policy_obj:
            total_policy = total_policy + 1
            # issueDate =policy.issueDate
            if policy_obj:
                issueDate = policy.issueDate
            else:
                issueDate = ""
        data = {
            "issueDate": issueDate,
            "agent_name": agent_name,
            "total_policy": total_policy,
            "ok_policy": total_policy
        }
        policy_data.append(data)
        grand_total_policy.append(total_policy)
    grand_policy = sum(grand_total_policy)
    return render(request, 'ledger/agent_payable.html', {'data': policy_data, 'datas': agent_obj, 'grand_policy': grand_policy})


def agent_statement(request):
    return render(request, 'ledger/agent_statement.html')


def sp_receivable(request):
    agent_obj = ServiceProvider.objects.filter(
        profile_id=get_id_from_session(request))
    policy_data = []
    grand_total_policy = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(sp_name=agent_name)
        total_policy = 0
        for policy in policy_obj:
            total_policy = total_policy + 1
            # issueDate =policy.issueDate
            if policy_obj:
                issueDate = policy.issueDate
            else:
                issueDate = ""
        data = {
            "issueDate": issueDate,
            "agent_name": agent_name,
            "total_policy": total_policy,
            "ok_policy": total_policy
        }
        policy_data.append(data)
        grand_total_policy.append(total_policy)
    grand_policy = sum(grand_total_policy)
    print(grand_policy)
    return render(request, 'ledger/SP_recevaible.html', {'data': policy_data, 'datas': agent_obj, 'grand_policy': grand_policy})


def sp_statement(request):
    return render(request, 'ledger/SP_statement.html')


def report_agent(request):
    agent_obj = Agents.objects.filter(status="Active")
    policy_data = []
    total_count_policy = []
    total_od = []
    total_tp = []
    total_net = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(agent_name=agent_name)
        count_policy = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD_premium = policy.OD_premium
            # total_od.append(OD_premium)
            TP_premium = policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy": count_policy,
            "agent_name": agent_name,
            "OD_premium": OD_premium,
            "TP_premium": TP_premium,
            "net": nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD_premium)
        total_tp.append(TP_premium)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_agent.html', {"datas": policy_data, "total_count_policy": total_count_policy, "total_od": total_od, "total_tp": total_tp, "total_net": total_net})


def report_policyprovider(request):
    agent_obj = ServiceProvider.objects.filter(
        profile_id=get_id_from_session(request))
    policy_data = []
    total_count_policy = []
    total_od = []
    total_tp = []
    total_net = []
    for agent in agent_obj:
        agent_name = agent.full_name
        policy_obj = Policy.objects.filter(sp_name=agent_name)
        count_policy = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            OD_premium = policy.OD_premium
            TP_premium = policy.TP_premium
            nett = policy.net
            data = {
                "count_policy": count_policy,
                "agent_name": agent_name,
                "OD_premium": OD_premium,
                "TP_premium": TP_premium,
                "net": nett,
            }
            policy_data.append(data)
            total_count_policy.append(count_policy)
            total_od.append(OD_premium)
            total_tp.append(TP_premium)
            total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_Policyprovider.html', {"datas": policy_data, "total_count_policy": total_count_policy, "total_od": total_od, "total_tp": total_tp, "total_net": total_net})


def report_vehicleCategory(request):
    agent_obj = VehicleCategory.objects.filter(
        profile_id=get_id_from_session(request))
    policy_data = []
    total_count_policy = []
    total_od = []
    total_tp = []
    total_net = []
    for agent in agent_obj:
        vc = agent.category
        policy_obj = Policy.objects.filter(vehicle_category=vc)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP = policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy": count_policy,
            "agent_name": vc,
            "OD_premium": OD,
            "TP_premium": TP,
            "net": nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_vehicalCategory.html', {"datas": policy_data, "total_count_policy": total_count_policy, "total_od": total_od, "total_tp": total_tp, "total_net": total_net})


def report_brokercode(request):
    agent_obj = BrokerCode.objects.filter(
        profile_id=get_id_from_session(request))
    policy_data = []
    total_count_policy = []
    total_od = []
    total_tp = []
    total_net = []
    for agent in agent_obj:
        broker = agent.code
        policy_obj = Policy.objects.filter(sp_brokercode=broker)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP = policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy": count_policy,
            "agent_name": broker,
            "OD_premium": OD,
            "TP_premium": TP,
            "net": nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_brokerCode.html', {"datas": policy_data, "total_count_policy": total_count_policy, "total_od": total_od, "total_tp": total_tp, "total_net": total_net})


def report_insurance_comp(request):
    agent_obj = InsuranceCompany.objects.filter(
        profile_id=get_id_from_session(request))
    policy_data = []
    total_count_policy = []
    total_od = []
    total_tp = []
    total_net = []
    for agent in agent_obj:
        inscomp = agent.comp_name
        policy_obj = Policy.objects.filter(insurance_comp=inscomp)
        count_policy = 0
        OD = 0
        TP = 0
        nett = 0
        for policy in policy_obj:
            count_policy = count_policy + 1
            # total_count_policy.append(count_policy)
            OD = policy.OD_premium
            # total_od.append(OD_premium)
            TP = policy.TP_premium
            # total_tp.append(TP_premium)
            nett = policy.net
            # total_net.append(nett)
        data = {
            "count_policy": count_policy,
            "agent_name": inscomp,
            "OD_premium": OD,
            "TP_premium": TP,
            "net": nett,
        }
        policy_data.append(data)
        total_count_policy.append(count_policy)
        total_od.append(OD)
        total_tp.append(TP)
        total_net.append(nett)
    total_od = sum(total_od)
    total_tp = sum(total_tp)
    total_net = sum(total_net)
    total_count_policy = sum(total_count_policy)
    return render(request, 'reports/report_insurance_company.html', {"datas": policy_data, "total_count_policy": total_count_policy, "total_od": total_od, "total_tp": total_tp, "total_net": total_net})


def subscription(request):
    return render(request, 'subscription.html')


def agent_profile(request):
    return render(request, 'agents/agent_particular.html')


def docs_download(request, id):
    print('docs_download method calling: ')

    file_key = 'media/documents/' + id
    save_in = os.path.join(MEDIA_ROOT, 'temp_file', id)

    print(file_key)

    print('FILE_KEY : ', file_key)
    print('save in : ', save_in)

    try:
        s3_client = boto3.client(
            's3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3_client.download_file(AWS_STORAGE_BUCKET_NAME, file_key,  save_in)
        print('File downloaded successfully.')
        # launch_pdf(save_in)
        return HttpResponse('')
    except Exception as e:
        print('Error downloading file:', str(e))
        return HttpResponse('Error downloading file: ' + str(e))


def launch_pdf(file_path):
    try:
        # subprocess.Popen(['open', file_path])  # For macOS
        # subprocess.Popen(['xdg-open', file_path])  # For Linux
        subprocess.Popen(['start', '', file_path], shell=True)  # For Windows
        print("PDF file launched successfully.")
    except Exception as e:
        print("Error launching PDF file:", str(e))


def download_pdf(request, id):
    print('download_pdf method calling: ')
    # Get the S3 storage instance
    s3_storage = S3Boto3Storage()

    # Specify the S3 file path of the PDF file
    # pdf_file_path = 'media/documents/000000002162902_PYP.pdf'  # Update with the actual path to your PDF file in the S3 bucket
    # Update with the actual path to your PDF file in the S3 bucket
    pdf_file_path = 'media/documents/' + id

    # Set the desired filename for the downloaded file
    filename = id

    # Generate the response with appropriate headers for file download
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Open the S3 file and read its contents
    with s3_storage.open(pdf_file_path) as pdf_file:
        response.write(pdf_file.read())

    return response


def store_deleted_policy(request, id):
    print('store_deleted_policy method calling:')

    try:
        values_list = Policy.objects.filter(policyid=id).values()
        # print(values_list)

        proposal_no = values_list[0]['proposal_no']
        policy_no = values_list[0]['policy_no']
        customer_name = values_list[0]['customer_name']
        insurance_company = values_list[0]['insurance_company']
        sp_name = values_list[0]['sp_name']
        sp_brokercode = values_list[0]['sp_brokercode']
        registration_no = values_list[0]['registration_no']
        rto_state = values_list[0]['rto_state']
        rto_city = values_list[0]['rto_city']
        vehicle_makeby = values_list[0]['vehicle_makeby']
        vehicle_model = values_list[0]['vehicle_model']
        vehicle_catagory = values_list[0]['vehicle_catagory']
        vehicle_fuel_type = values_list[0]['vehicle_fuel_type']
        mfg_year = values_list[0]['mfg_year']
        addon = values_list[0]['addon']
        ncb = values_list[0]['ncb']
        cubic_capacity = values_list[0]['cubic_capacity']
        gvw = values_list[0]['gvw']
        seating_capacity = values_list[0]['seating_capacity']
        coverage_type = values_list[0]['coverage_type']
        policy_type = values_list[0]['policy_type']
        cpa = values_list[0]['cpa']
        risk_start_date = values_list[0]['risk_start_date']
        risk_end_date = values_list[0]['risk_end_date']
        issue_date = values_list[0]['issue_date']
        insured_age = values_list[0]['insured_age']
        policy_term = values_list[0]['policy_term']
        bqp = values_list[0]['bqp']
        pos = values_list[0]['pos']
        employee = values_list[0]['employee']
        remark = values_list[0]['remark']

        OD_premium = values_list[0]['OD_premium']
        TP_terrorism = values_list[0]['TP_terrorism']
        net = values_list[0]['net']
        gst_amount = values_list[0]['gst_amount']
        gst_gcv_amount = values_list[0]['gst_gcv_amount']
        total = values_list[0]['total']
        payment_mode = values_list[0]['payment_mode']

        proposal = values_list[0]['proposal']
        mandate = values_list[0]['mandate']
        policy = values_list[0]['policy']
        previous_policy = values_list[0]['previous_policy']
        pan_card = values_list[0]['pan_card']
        aadhar_card = values_list[0]['aadhar_card']
        vehicle_rc = values_list[0]['vehicle_rc']
        inspection_report = values_list[0]['inspection_report']

        pol = DeletedPolicy.objects.create(proposal_no=proposal_no, policy_no=policy_no,  customer_name=customer_name, insurance_company=insurance_company, sp_name=sp_name,
                                           sp_brokercode=sp_brokercode,  registration_no=registration_no,
                                           rto_state=rto_state, rto_city=rto_city,  vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model, vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type,
                                           mfg_year=mfg_year,
                                           addon=addon, ncb=ncb, cubic_capacity=cubic_capacity, gvw=gvw, seating_capacity=seating_capacity, coverage_type=coverage_type, policy_type=policy_type, cpa=cpa,
                                           risk_start_date=risk_start_date,
                                           risk_end_date=risk_end_date, issue_date=issue_date, insured_age=insured_age, policy_term=policy_term,  bqp=bqp, pos=pos,
                                           employee=employee,
                                           OD_premium=OD_premium, TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount, gst_gcv_amount=gst_gcv_amount,
                                           total=total, payment_mode=payment_mode,
                                           proposal=proposal, mandate=mandate,
                                           policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card,
                                           vehicle_rc=vehicle_rc, inspection_report=inspection_report,
                                           remark=remark)

        print('policy saved: ', pol)
        Policy.objects.get(policyid=id).delete()
        print('policy deleted: ', pol)

        return redirect('bima_policy:policy_entry')

    except Exception as e:
        print("Error occurred in store_deleted_policy:", str(e))
        return HttpResponse("Error occurred in store_deleted_policy: " + str(e))


def policy_deleted_entry(request):
    try:
        print('policy_deleted_entry method')
        print(get_id_from_session(request))

        agent_list = []
        datag = Agents.objects.filter(status="Active").values('full_name')
        for ag in datag:
            agent_list.append(ag['full_name'])

        context = read_vehicle_data_file()
        make = context["make"]
        model = context["model"]

        datacat_list = []
        data_cat = VehicleCategory.objects.all().values()
        for vc in data_cat:
            datacat_list.append(vc["category"])

        datavm = VehicleModelName.objects.all().values()
        datavmb = VehicleMakeBy.objects.all().values()

        for vm in datavm:
            model.append(vm["model"])

        for vmb in datavmb:
            make.append(vmb["company"])

        data = DeletedPolicy.objects.order_by('-policyid').values()

        return render(request, 'policylist/policy_entry_list deleted.html', {"agent_list": agent_list, "vdata": context, "data_cat": datacat_list, 'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})
        # return render(request, 'policylist/policy_entry_list.html', { "agent_list": agent_list, "vdata": context, "data_cat": datacat_list, 'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as e:
        print("Error occurred in policy_deleted_entry:", str(e))
        return HttpResponse("Error occurred in policy_deleted_entry: " + str(e))


def policy_local_entry(request):
    try:
        print('policy_local_entry method')
        print(get_id_from_session(request))

        # data = DeletedPolicy.objects.order_by('-policyid').values()

        return render(request, 'policylist/policy_entry_local_list.html')
        # return render(request, 'policylist/policy_entry_list.html', { "agent_list": agent_list, "vdata": context, "data_cat": datacat_list, 'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as e:
        print("Error occurred in policy_deleted_entry:", str(e))
        return HttpResponse("Error occurred in policy_deleted_entry: " + str(e))


def set_payout(data, id):
    try:
        print('set_payout method calling: ')

        reg = data.registration_no[0:4]

        # data1 = Payout.objects.filter(Q(insurance_company__icontains=data.insurance_company) &
        #                               Q(sp_name__icontains=data.sp_name) &
        #                               Q(sp_brokercode__icontains=data.sp_brokercode) &
        #                               Q(vehicle_makeby__icontains=data.vehicle_makeby) &

        #                               Q(vehicle_fuel_type__icontains=data.vehicle_fuel_type) &
        #                               Q(mfg_year__icontains=data.mfg_year) &
        #                               Q(rto_city__icontains=reg) &
        #                               Q(addon__icontains=data.addon) &
        #                               Q(ncb__icontains=data.ncb) &

        #                               Q(policy_type__icontains=data.policy_type) &
        #                               Q(policy_term__icontains=data.policy_term) &
        #                               Q(cpa__contains=data.cpa))

        data1 = Payout.objects.filter(insurance_company__icontains=data.insurance_company,
                                      sp_name__icontains=data.sp_name,
                                      sp_brokercode__icontains=data.sp_brokercode,
                                      vehicle_makeby__icontains=data.vehicle_makeby,
                                      vehicle_fuel_type__icontains=data.vehicle_fuel_type,
                                      mfg_year__icontains=data.mfg_year,
                                      rto_city__icontains=reg,
                                      addon__icontains=data.addon,
                                      ncb__icontains=data.ncb,
                                      policy_type__icontains=data.policy_type,
                                      policy_term__icontains=data.policy_term,
                                      cpa__contains=data.cpa)

        if data.vehicle_catagory == 'TWO WHEELER' or data.vehicle_catagory == 'TWO WHEELER SCOOTER' or data.vehicle_catagory == 'TWO WHEELER BIKE' or data.vehicle_catagory == 'PRIVATE CAR' or data.vehicle_catagory == 'TRADE RISK':
            data1 = data1.filter(
                cubic_capacity__icontains=data.cubic_capacity)[0]

        elif data.vehicle_catagory == 'TWO WHEELER COMMERCIAL' or data.vehicle_catagory == 'TAXI 4 WHEELER':
            data1 = data1.filter(cubic_capacity__icontains=data.cubic_capacity,
                                 seating_capacity__icontains=data.seating_capacity)[0]

        elif data.vehicle_catagory == 'GCV-PUBLIC CARRIER OTHER THAN 3 W':
            data1 = data1.filter(gvw__icontains=data.gvw)[0]

        elif data.vehicle_catagory == '3 WHEELER PCV' or data.vehicle_catagory == 'BUS AND OTHERS' or data.vehicle_catagory == 'MISC-D SPECIAL VEHICLE' or data.vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME' or data.vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
            data1 = data1.filter(
                seating_capacity__icontains=data.seating_capacity)[0]

        elif data.vehicle_catagory == '3 WHEELER GCV-PUBLIC CARRIER':
            data1 = data1.filter(
                gvw__icontains=data.gvw, seating_capacity__icontains=data.seating_capacity)[0]

        if fix_special_chars_from_vehicle_modelp(data.vehicle_model, data1) is not None:
            if fix_special_chars_from_coverage_typep(data.coverage_type, data1) is not None:

                agent_od_reward = float(data1.agent_od_reward)
                agent_od_amount = round(
                    (float(data.OD_premium) * agent_od_reward) / 100, 2)
                agent_tp_reward = float(data1.agent_tp_reward)
                agent_tp_amount = round(
                    (float(data.TP_terrorism) * agent_tp_reward) / 100, 2)
                # Self payout
                self_od_reward = float(data1.self_od_reward)
                self_od_amount = round(
                    (float(data.OD_premium) * self_od_reward) / 100, 2)
                self_tp_reward = float(data1.self_tp_reward)
                self_tp_amount = round(
                    (float(data.TP_terrorism) * self_tp_reward) / 100, 2)

                pol = Policy.objects.filter(policyid=id)

                pol.update(agent_od_reward=agent_od_reward,
                           agent_od_amount=agent_od_amount,
                           agent_tp_reward=agent_tp_reward,
                           agent_tp_amount=agent_tp_amount,

                           self_od_reward=self_od_reward,
                           self_od_amount=self_od_amount,
                           self_tp_reward=self_tp_reward,
                           self_tp_amount=self_tp_amount)

        print('payout applied')

        return ''

    except Exception as ex:
        print('apply_policy : ', str(ex))
        return ('apply_policy : ' + str(ex))


def send_otp(otp):
    print('send_otp calling')
    try:
        to = settings.TWILIO_PHONE_TO
        send_otp_via_twilio(to, otp)
        return ''
    except Exception as ex:
        return str(ex)


def send_otp_via_twilio(to, otp):
    return ''
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=f"Your OTP: {otp}",
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=to
    # )
    # return message.sid


def new_entry(request):
    try:
        print('new_entry method')

        id = get_profile_id(get_id_from_session(request))
        profile_id = ProfileModel.objects.get(id=id)

        ptype = request.POST['ptype']
        print(ptype)
        policyid = request.POST['policyid']
        policy_no = request.POST['policy_no']

        if ptype == "motor":
            if policyid != "":
                print('motor update: ')
                data = Policy.objects.filter(policyid=policyid)
                print(data)
                data.update(proposal_no=request.POST['proposal_no'],
                            policy_no=request.POST['policy_no'],
                            customer_name=request.POST['customer_name'],
                            insurance_company=request.POST['insurance_company'],
                            sp_name=request.POST['sp_name'],
                            sp_brokercode=request.POST['sp_brokercode'],
                            registration_no=request.POST['registration_no'],
                            rto_state=request.POST['rto_state'],
                            rto_city=request.POST['rto_city'],
                            vehicle_makeby=request.POST['vmake'],
                            vehicle_model=request.POST['vmodel'],
                            vehicle_catagory=request.POST['vehicle_catagory'],
                            vehicle_fuel_type=request.POST['vehicle_fuel_type'],
                            mfg_year=request.POST['mfg_year'],
                            addon=request.POST['addon'],
                            ncb=request.POST['ncb'],
                            cubic_capacity=request.POST['cubic_capacity'],
                            coverage_type=request.POST['coverage_type'],
                            seating_capacity=request.POST['seating_capacity'],
                            gvw=request.POST['gvw'],
                            policy_type=request.POST['policy_type'],
                            cpa=request.POST['cpa'],
                            risk_start_date=request.POST['risk_start_date'],
                            risk_end_date=request.POST['risk_end_date'],
                            issue_date=request.POST['issue_date'],
                            insured_age=request.POST['insured_age'],
                            policy_term=request.POST['policy_term'],
                            bqp=request.POST['bqp'],
                            pos=request.POST['pos'],
                            employee=get_id_from_session(request),
                            remark=request.POST['remark'],
                            OD_premium=request.POST['od'],
                            TP_terrorism=request.POST['tpt'],
                            net=request.POST['net'],
                            total=request.POST['total'],
                            gst_amount=request.POST['gst'],
                            gst_gcv_amount=request.POST['gstt'],
                            payment_mode=request.POST['payment_mode']
                            )

                print('done')
                return JsonResponse('done: ' + policy_no, safe=False)

            else:
                print('motor new')
                my_model = Policy.objects.create(profile_id=profile_id,
                                                 proposal_no=request.POST['proposal_no'],
                                                 policy_no=request.POST['policy_no'],
                                                 customer_name=request.POST['customer_name'],
                                                 insurance_company=request.POST['insurance_company'],
                                                 sp_name=request.POST['sp_name'],
                                                 sp_brokercode=request.POST['sp_brokercode'],
                                                 registration_no=request.POST['registration_no'],
                                                 rto_state=request.POST['rto_state'],
                                                 rto_city=request.POST['rto_city'],
                                                 vehicle_makeby=request.POST['vmake'],
                                                 vehicle_model=request.POST['vmodel'],
                                                 vehicle_catagory=request.POST['vehicle_catagory'],
                                                 vehicle_fuel_type=request.POST['vehicle_fuel_type'],
                                                 mfg_year=request.POST['mfg_year'],
                                                 addon=request.POST['addon'],
                                                 ncb=request.POST['ncb'],
                                                 cubic_capacity=request.POST['cubic_capacity'],
                                                 coverage_type=request.POST['coverage_type'],
                                                 seating_capacity=request.POST['seating_capacity'],
                                                 gvw=request.POST['gvw'],
                                                 policy_type=request.POST['policy_type'],
                                                 cpa=request.POST['cpa'],
                                                 risk_start_date=request.POST['risk_start_date'],
                                                 risk_end_date=request.POST['risk_end_date'],
                                                 issue_date=request.POST['issue_date'],
                                                 insured_age=request.POST['insured_age'],
                                                 policy_term=request.POST['policy_term'],
                                                 bqp=request.POST['bqp'],
                                                 pos=request.POST['pos'],
                                                 employee=get_id_from_session(
                                                     request),
                                                 remark=request.POST['remark'],
                                                 OD_premium=request.POST['od'],
                                                 TP_terrorism=request.POST['tpt'],
                                                 net=request.POST['net'],
                                                 total=request.POST['total'],
                                                 gst_amount=request.POST['gst'],
                                                 gst_gcv_amount=request.POST['gstt'],
                                                 payment_mode=request.POST['payment_mode'],

                                                 proposal=request.POST['proposal'],
                                                 mandate=request.POST['mandate'],
                                                 policy=request.POST['policy'],
                                                 previous_policy=request.POST['previous_policy'],
                                                 pan_card=request.POST['pan_card'],
                                                 aadhar_card=request.POST['aadhar_card'],
                                                 vehicle_rc=request.POST['vehicle_rc'],
                                                 inspection_report=request.POST['inspection_report']
                                                 )

                return JsonResponse('done: ' + policy_no, safe=False)

        else:
            if policyid != "":
                print('non motor update')
                data = update_entry_non_motor(request, policyid)
                print(data)
                return JsonResponse('done: ' + policy_no, safe=False)

            else:
                print('non motor new')
                data = new_entry_non_motor(request)
                print(data)
            return JsonResponse('done: ' + policy_no, safe=False)

    except Exception as e:
        print("Error occurred in new_entry method:", str(e))
        return JsonResponse('error: ' + request.POST['policy_no'], safe=False)


def new_entry_non_motor(request):
    try:
        print('new_entry_non_motorr method')

        id = get_profile_id(get_id_from_session(request))
        profile_id = ProfileModel.objects.get(id=id)

        print(request.POST['policy_no'])

        data = Policy.objects.create(profile_id=profile_id,
                                     product_name=request.POST['product_name'],
                                     policy_type=request.POST['policy_type'],
                                     proposal_no=request.POST['proposal_no'],
                                     policy_no=request.POST['policy_no'],
                                     customer_name=request.POST['customer_name'],
                                     insurance_company=request.POST['insurance_company'],
                                     sp_name=request.POST['sp_name'],
                                     sp_brokercode=request.POST['sp_brokercode'],
                                     risk_start_date=request.POST['risk_start_date'],
                                     risk_end_date=request.POST['risk_end_date'],
                                     issue_date=request.POST['issue_date'],
                                     policy_term=request.POST['policy_term'],
                                     bqp=request.POST['bqp'],
                                     pos=request.POST['pos'],
                                     employee=get_id_from_session(request),

                                     proposal=request.POST['proposal'],
                                     mandate=request.POST['mandate'],
                                     policy=request.POST['policy'],
                                     previous_policy=request.POST['previous_policy'],
                                     pan_card=request.POST['pan_card'],
                                     aadhar_card=request.POST['aadhar_card'],
                                     #  vehicle_rc=request.POST['vehicle_rc'],
                                     inspection_report=request.POST['inspection_report'],

                                     OD_premium=request.POST['od'],
                                     TP_terrorism=request.POST['tpt'],
                                     net=request.POST['net'],
                                     gst_amount=request.POST['gst'],
                                     total=request.POST['total'],
                                     payment_mode=request.POST['payment_mode'],
                                     remark=request.POST['remark'])

        print('pol data ', data)

        return data
    except Exception as e:
        print("Error occurred in new_entry_non_motor method:", str(e))
        return str(e)


def update_entry_non_motor(request, policyid):
    try:
        print('new_entry_non_motorr method')

        print('in update block: ')
        data = Policy.objects.filter(policyid=policyid)
        print(data)
        data.update(product_name=request.POST['product_name'],
                    policy_type=request.POST['policy_type'],
                    proposal_no=request.POST['proposal_no'],
                    policy_no=request.POST['policy_no'],
                    customer_name=request.POST['customer_name'],
                    insurance_company=request.POST['insurance_company'],
                    sp_name=request.POST['sp_name'],
                    sp_brokercode=request.POST['sp_brokercode'],
                    risk_start_date=request.POST['risk_start_date'],
                    risk_end_date=request.POST['risk_end_date'],
                    issue_date=request.POST['issue_date'],
                    policy_term=request.POST['policy_term'],
                    bqp=request.POST['bqp'],
                    pos=request.POST['pos'],
                    employee=get_id_from_session(request),
                    OD_premium=request.POST['od'],
                    TP_terrorism=request.POST['tpt'],
                    net=request.POST['net'],
                    gst_amount=request.POST['gst'],
                    total=request.POST['total'],
                    payment_mode=request.POST['payment_mode'],
                    remark=request.POST['remark'])

        print('done')
        return data

    except Exception as e:
        print("Error occurred in new_entry_non_motor method:", str(e))
        return str(e)

def generate_random_filename():
    unique_filename = str(uuid.uuid4()).replace("/", "").replace("-", "")
    return unique_filename

def new_posp(request):
    try:
        print('new_posp method')

        id = get_profile_id(get_id_from_session(request))
        profile_id = ProfileModel.objects.get(id=id)

        login_id = request.POST['login_id']
        posp_code = request.POST['posp_code']

        if login_id != "":
            print('login_id ', login_id)           
                       
            data = Agents.objects.filter(login_id=login_id)  

            my_model = data.update(posp_code=request.POST['posp_code'],
                                   registration_code=request.POST['registration_code'],
                                   full_name=request.POST['full_name'],
                                   gender=request.POST['gender'],
                                   mob_no=request.POST['mob_no'],
                                   email_id=request.POST['email_id'],
                                   address=request.POST['address'],
                                   state=request.POST['state'],
                                   city=request.POST['city'],
                                   pincode=request.POST['pincode'],
                                   rural_urban=request.POST['rural_urban'],
                                   slab=request.POST['slab'],
                                   GSTIN=request.POST['GSTIN'],
                                   account_no=request.POST['account_no'],
                                   ifsc_code=request.POST['ifsc_code'],
                                   bank_name=request.POST['bank_name'],

                                    # basic_qualification= basic_qualification,
                                    # aadhar_card=aadhar_card,
                                    # pan_card=pan_card,
                                    # training_certificate=training_certificate,
                                    # appointment_certificate=appointment_certificate,
                                    # agreement_certificate=agreement_certificate,
                                    # bank_details=bank_details,
                                 
                                #    password=request.POST['password'],
                                   created_by=get_id_from_session(request)
            )
            
            print('model : ' , my_model)

            fspr =  FileSystemStorage()
            basic_qualification = request.FILES.get('basic_qualification')           
            print('basic_qualification: ', basic_qualification)          
        
            data = Agents.objects.filter(login_id=login_id)              

            if basic_qualification is not None:
                bq = fspr.save('media/documents/' + basic_qualification.name, basic_qualification)
                print('bq: ', bq)
                num = data.update(basic_qualification =  bq)
                print('num is:', num)

                data = Agents.objects.filter(login_id=login_id)  
                print(data[0])
                print(data[0].basic_qualification)

            else: basic_qualification = data[0].basic_qualification                 
            
           
            return JsonResponse({"done":  posp_code})
            
            # fspr = FileSystemStorage()

            # basic_qualification = request.FILES.get('basic_qualification')         
            # print(basic_qualification)

            # if basic_qualification is not None:          
            #     tmp_name = generate_random_filename() + basic_qualification.name    
            #     fspr.save(tmp_name   , basic_qualification)           
            #     basic_qualification = 'media/documents/' + tmp_name      
            # else:
            #     basic_qualification = data[0].basic_qualification

            # print(data[0].basic_qualification)                                

            # return JsonResponse('done: ' + posp_code, safe=False)
            # return JsonResponse({"done":  posp_code})
        

        else:
            print('login_id ', login_id)

            fspr = FileSystemStorage()

            basic_qualification = request.FILES.get('basic_qualification')
            aadhar_card = request.FILES.get('aadhar_card')
            pan_card = request.FILES.get('pan_card')
            training_certificate = request.FILES.get('training_certificate')
            appointment_certificate = request.FILES.get('appointment_certificate')
            agreement_certificate = request.FILES.get('agreement_certificate')
            bank_details = request.FILES.get('bank_details')
            
            # print(basic_qualification)

            if basic_qualification is not None:
                fspr.save(basic_qualification.name, basic_qualification)
            if aadhar_card is not None:
                fspr.save(aadhar_card.name, aadhar_card)
            if pan_card is not None:
                fspr.save(pan_card.name, pan_card)
            if training_certificate is not None:
                fspr.save(training_certificate.name, training_certificate)
            if appointment_certificate is not None:
                fspr.save(appointment_certificate.name, appointment_certificate)
            if agreement_certificate is not None:
                fspr.save(agreement_certificate.name, agreement_certificate)
            if bank_details is not None:
                fspr.save(bank_details.name, bank_details)
                       
            my_model = Agents.objects.create(profile_id=profile_id,
                                             posp_code=request.POST['posp_code'],
                                             registration_code=request.POST['registration_code'],
                                             full_name=request.POST['full_name'],
                                             gender=request.POST['gender'],
                                             mob_no=request.POST['mob_no'],
                                             email_id=request.POST['email_id'],
                                             address=request.POST['address'],
                                             state=request.POST['state'],
                                             city=request.POST['city'],
                                             pincode=request.POST['pincode'],
                                             rural_urban=request.POST['rural_urban'],
                                             slab=request.POST['slab'],
                                             GSTIN=request.POST['GSTIN'],
                                             account_no=request.POST['account_no'],
                                             ifsc_code=request.POST['ifsc_code'],
                                             bank_name=request.POST['bank_name'],

                                             basic_qualification=basic_qualification,
                                             aadhar_card=aadhar_card,
                                             pan_card=pan_card,
                                             training_certificate=training_certificate,
                                             appointment_certificate=appointment_certificate,
                                             agreement_certificate=agreement_certificate,
                                             bank_details=bank_details,

                                             password=request.POST['password'],
                                             created_by=get_id_from_session(
                                                 request)
                                             )

            print(my_model)

            # return JsonResponse('done: ' + posp_code, safe=False)
            return JsonResponse({"done":  posp_code})

    except Exception as e:
        print("Error occurred in new_posp method:", str(e))
        # return JsonResponse('error: ' + posp_code + ' : ' + str(e), safe=False)
        return JsonResponse({'error' :  posp_code })


def delete_policy(request):
    try:
        print('delete policy is calling...')
        data = request.GET.get('data')
        print(data)
        val = Policy.objects.get(policyid=data).delete()
        print(val)
        return JsonResponse({'message': "deleted"})
    except Exception as e:
        print('error occured when deleting policy: ' + str(e))
        return JsonResponse({'message': str(e)})


def delete_posp(request):
    try:
        print('delete posp is calling...')
        data = request.GET.get('data')
        print(data)
        val = Agents.objects.get(login_id=data).delete()
        print(val)
        return JsonResponse({'message': "deleted"})
    except Exception as e:
        print('error occured when deleting posp: ' + str(e))
        return JsonResponse({'message': str(e)})


def add_vehicle(request):
    try:
        print('add_vehicle is calling...')       
        data = json.loads(request.GET.get('data'))
        # print(data)      
        # print(data['choice'])
        # print(data['name'])

        if data['choice'] == "category":
            vm = VehicleCategory.objects.filter(category=data['name'] )
            # print(vm)
            if vm.__len__()== 0:
                obj = VehicleCategory.objects.create( category=data['name'], created_by=get_id_from_session(request), status=data['status'])
                # print(obj)
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' added!'})
            else:                
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' already exist!'})
        
        if data['choice'] == "make":
            vm = VehicleMake.objects.filter(make=data['name'] )
            # print(vm)
            if vm.__len__()== 0:
                obj = VehicleMake.objects.create( make=data['name'], created_by=get_id_from_session(request), status=data['status'])
                # print(obj)
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' added!'})

            else:                
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' already exist!'})

        if data['choice'] == "model":
            vm = VehicleModel.objects.filter(model=data['name'] )
            # print(vm)
            if vm.__len__()== 0:
                obj = VehicleModel.objects.create( model=data['name'], created_by=get_id_from_session(request), status=data['status'])
                # print(obj)
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' added!'})
            else:                
                return JsonResponse({'data': data['choice'] + ': ' + data['name'] + ' already exist!'})
        
        return JsonResponse({'data': 'Nothing!'})
        
    except Exception as e:
        print('error occured when deleting posp: ' + str(e))
        return JsonResponse({'message': str(e)})

