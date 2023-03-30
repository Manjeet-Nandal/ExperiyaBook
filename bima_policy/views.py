import json
from dateutil import parser
from django.utils import timezone
from datetime import datetime, timedelta
from dataclasses import dataclass
from datetime import datetime
import django
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View

from Bima.settings import MEDIA_ROOT
from .models import *
from .forms import *
from django.db.models import Q
from django.core.paginator import Paginator

def get_id_from_session(request):
    id = request.session['id']
    return id


def is_user(request):
    return len(get_id_from_session(request)) == 15


def Index(request):
    return render(request, 'index.html')


# DashBoardView
def dashboard(request):
    agentcount = Agents.objects.filter(
        profile_id=get_id_from_session(request)).count()
    staffcount = StaffModel.objects.filter(
        profile_id=get_id_from_session(request)).count()
    spcount = ServiceProvider.objects.filter(
        profile_id=get_id_from_session(request)).count()
    policycount = Agents.objects.filter(
        profile_id=get_id_from_session(request)).count()
    print('total agents are:', agentcount)
    return render(request, 'dashboard.html', {'agentcount': agentcount, 'staffcount': staffcount, 'spcount': spcount, 'totalpolicy': policycount})


# LoginView
def login_form(request):
    return render(request, 'login.html')


def loginView(request):
    try:
        if request.method == 'POST':
            full_name = request.POST['full_name']
            password = request.POST['password']
            user = ProfileModel.objects.filter(
                full_name=full_name, password=password).first()
            user1 = Agents.objects.filter(
                login_id=full_name, password=password).first()
            user2 = StaffModel.objects.filter(
                login_id=full_name, password=password).first()
            if user:
                p = ProfileModel.objects.filter(
                    full_name=full_name, password=password).first()
                id = p.id
                request.session['id'] = user.id
                request.session['full_name'] = user.full_name
                userr_ob = UserRole.objects.filter(profile_id=id)
                if userr_ob:
                    pass
                else:
                    UserRole.objects.create(profile_id_id=id, role='admin')
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


# UserView
def staffmanage(request):
    if request.method == 'GET':
        try:
            data = StaffModel.objects.filter(
                profile_id=get_id_from_session(request))
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
    if request.method == 'GET':
        try:
            data = StaffModel.objects.filter(login_id=id)
            return render(request, 'user/user_edit.html', {'data': data})
        except StaffModel.DoesNotExist:
            return render(request, 'user/user_edit.html')
    else:
        if 'profile' in request.POST:
            StaffModel.objects.filter(login_id=id).update(
                staffname=request.POST['full_name'], status=request.POST['status'])
        return redirect('bima_policy:staff')


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


def change_password(request):
    if request.method == 'POST' and 'updpassword' in request.POST:
        profile = ProfileModel.objects.filter(id=get_id_from_session(request))
        password = request.POST['password']
        profile.update(password=password)


# RTOView
def rto_list(request):
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


def update_rto(request, id):
    data = {}
    if request.method == "GET":
        data = RtoConversionModel.objects.filter(
            profile_id_id=get_id_from_session(request))
        udata = RtoConversionModel.objects.filter(id=id)
        return render(request, 'RTO.html', {'data': data, 'udata': udata})
    if request.method == 'POST':
        if "delete" in request.POST:
            item = get_object_or_404(RtoConversionModel, id=id)
            item.delete()
            return redirect('bima_policy:rto')


# InsuranceView
def ins_comp(request):
    print('ins_comp')
    if request.method == "GET":
        try:
            data = InsuranceCompany.objects.filter(
                profile_id=get_id_from_session(request))
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


# VehicleView
def vehicle_view(request):
    if request.method == "GET":
        try:
            data = VehicleMakeBy.objects.filter(
                profile_id_id=get_id_from_session(request))
            datamn = VehicleModelName.objects.filter(
                profile_id_id=get_id_from_session(request))
            datavc = VehicleCategory.objects.filter(
                profile_id_id=get_id_from_session(request))
            mylist = zip(datamn, data)
            return render(request, 'vehicle/vehicle.html', {'list': mylist, 'datavc': datavc, 'data': data, 'datamn': datamn})
        except(VehicleMakeBy.DoesNotExist, VehicleModelName.DoesNotExist, VehicleCategory.DoesNotExist):
            return render(request, 'vehicle/vehicle.html')
    else:
        p = ProfileModel.objects.get(id=get_id_from_session(request))
        if 'mb_add' in request.POST:
            VehicleMakeBy.objects.create(
                company=request.POST['makeby'], status=request.POST['mbstatus'], profile_id=p)
            return redirect('bima_policy:vehi')
        elif 'vm_add' in request.POST:
            VehicleModelName.objects.create(
                model=request.POST['model'], status=request.POST['vmstatus'], profile_id=p)
            return redirect('bima_policy:vehi')
        elif 'vc_add' in request.POST:
            VehicleCategory.objects.create(
                category=request.POST['category'], status=request.POST['vcstatus'], profile_id=p)
            return redirect('bima_policy:vehi')
        return redirect('bima_policy:vehi')


def delete_vehicle(request, id):
    if request.method == "POST" and 'delete' in request.POST:
        data1 = VehicleCategory.objects.filter(id=id)
        data2 = VehicleMakeBy.objects.filter(id=id)
        data3 = VehicleModelName.objects.filter(id=id)
        if data1:
            data1.delete()
        elif data2:
            data2.delete()
        elif data3:
            data3.delete()
        return redirect('bima_policy:vehi')
    elif request.method == "POST" and 'edit' in request.POST:
        return edit_vehicle(request, id)


def edit_vehicle(request, id):
    vcd = VehicleCategory.objects.filter(id=id)
    vmbd = VehicleMakeBy.objects.filter(id=id)
    vmd = VehicleModelName.objects.filter(id=id)
    if request.method == "GET":
        if vcd:
            data = VehicleCategory.objects.filter(id=id)
            return render(request, 'vehicle/vehicle_edit.html', {'data': data})
        elif vmbd:
            data = VehicleMakeBy.objects.filter(id=id)
            return render(request, 'vehicle/vmb_edit.html', {'data': data})
        elif vmd:
            data1 = VehicleModelName.objects.filter(id=id)
            data = VehicleMakeBy.objects.filter(
                profile_id=get_id_from_session(request))
            return render(request, 'vehicle/vm_edit.html', {'data': data, 'data1': data1})

    if request.method == 'POST':
        if 'vc_update' in request.POST:
            category = request.POST['category']
            status_update = request.POST['status_update']
            VehicleCategory.objects.filter(id=id).update(
                category=category, status=status_update)
            return redirect('bima_policy:vehi')
        if 'vmb_update' in request.POST:
            company = request.POST['company']
            status_update = request.POST['status_update']
            VehicleMakeBy.objects.filter(id=id).update(
                company=company, status=status_update)
            return redirect('bima_policy:vehi')
        if 'vm_update' in request.POST:
            company = request.POST.get('company')
            model = request.POST['model']
            status_update = request.POST['status_update']
            VehicleModelName.objects.filter(id=id).update(
                company=company, model=model, status=status_update)
            return redirect('bima_policy:vehi')


# ServiceProviderView
def service_provider(request):
    if request.method == "GET":
        try:
            brokerdata = BrokerCode.objects.filter(
                profile_id=get_id_from_session(request))
            data = ServiceProvider.objects.filter(
                profile_id=get_id_from_session(request))
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
    except Exception as ex:
        login_id = StaffModel.objects.get(login_id=id).profile_id
    return ProfileModel.objects.get(id=login_id).id


class create_policy(View):
    def get(self, request):
        print('create_policy get method')
        pid = get_profile_id(get_id_from_session(request))
        data_ag = json.dumps(list(Agents.objects.filter(profile_id=pid).values()))
        data_sp = ServiceProvider.objects.filter(profile_id=pid)
        data_bc = BrokerCode.objects.filter(profile_id=pid)
        data_ins = InsuranceCompany.objects.filter(profile_id=pid)
        data_vmb = VehicleMakeBy.objects.filter(profile_id=pid)
        data_vm = VehicleModelName.objects.filter(profile_id=pid)
        data_vc = VehicleCategory.objects.filter(profile_id=pid)
        data_ct = CoverageType.objects.filter(profile_id=pid)
        data_bqp = BQP.objects.filter(profile_id=pid)
        # print(datag)

        return render(request, 'policylist/policy_list.html', {'is_motor_form': True, 'data_ag': data_ag,  'data_sp': data_sp, 'data_bc': data_bc, 'data_ins': data_ins, 'data_vmb': data_vmb, 'data_vm': data_vm, 'data_vc': data_vc, 'data_ct': data_ct, 'data_bqp': data_bqp})

    def post(self, request):
        print('create_policy post method')
        
        profile_id = ProfileModel.objects.get(
            id=get_profile_id(get_id_from_session(request)))
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
        cpa = request.POST['cpa']
        risk_start_date = request.POST['risk_start_date']
        risk_end_date = request.POST['risk_end_date']
        issue_date = request.POST['issue_date']
        try:
            insured_age = request.POST['insured_age']
        except:
            insured_age = 0
        policy_term = request.POST['policy_term']
        bqp = request.POST['bqp']
        pos = request.POST['pos']
        employee = request.POST['employee']
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
        
        # print(vehicle_catagory)
        if vehicle_catagory == 'TWO WHEELER':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(rto_city__contains=reg) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(cubic_capacity__contains=cubic_capacity) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)
                                             ).values()
                print('data ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'PRIVATE CAR':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(cubic_capacity__contains=cubic_capacity) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'GCV-PUBLIC CARRIER OTHER THAN 3 W':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(gvw__contains=gvw) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == '3 WHEELER PCV':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == '3 WHEELER GCV-PUBLIC CARRIER':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(gvw__contains=gvw) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'TAXI 4 WHEELER':
            try:
                reg = registration_no[0:4]
                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(cubic_capacity__contains=cubic_capacity) &
                                             Q(seating_capacity__contains=seating_capacity) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

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

                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(seating_capacity__contains=cap) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'MISC-D SPECIAL VEHICLE':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME':
            try:
                reg = registration_no[0:4]
                print('cap ', reg)

                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)
        elif vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
            try:
                reg = registration_no[0:4]

                data = Payout.objects.filter(Q(insurance_company__contains=insurance_company) &
                                             Q(sp_name__contains=sp_name) &
                                             Q(sp_brokercode__contains=sp_brokercode) &
                                             Q(vehicle_makeby__contains=vehicle_makeby) &
                                             Q(vehicle_model__contains=vehicle_model) &
                                             Q(vehicle_catagory__contains=vehicle_catagory) &
                                             Q(vehicle_fuel_type__contains=vehicle_fuel_type) &
                                             Q(mfg_year__contains=mfg_year) &
                                             Q(rto_city__contains=reg) &
                                             Q(addon__contains=addon) &
                                             Q(ncb__contains=ncb) &
                                             Q(coverage_type__contains=coverage_type) &
                                             Q(policy_type__contains=policy_type) &
                                             Q(policy_term__contains=policy_term) &
                                             Q(cpa__contains=cpa)).values()
                print('data is ', data)

            except Exception as ex:
                print(ex)

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
                                    policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card, vehicle_rc=vehicle_rc, inspection_report=inspection_report
                                    )
       
        return render(request, 'policylist/list_apply_payout.html', {'data':data,'policyid':pol.policyid})


class create_policy_non_motor(View):
    def get(self, request):
        print('create_policy Non get')
        pid = get_profile_id(get_id_from_session(request))
        data_ag = json.dumps(list(Agents.objects.filter(profile_id=pid).values()))
        data_sp = ServiceProvider.objects.filter(profile_id=pid)
        data_bc = BrokerCode.objects.filter(profile_id=pid)
        data_ins = InsuranceCompany.objects.filter(profile_id=pid)
        data_bqp = BQP.objects.filter(profile_id=pid)

        return render(request, 'policylist/policy_list.html', {'is_motor_form': False,  'data_ag': data_ag, 'data_sp': data_sp, 'data_bc': data_bc, 'data_ins': data_ins,  'data_bqp': data_bqp})

    def post(self, request):
        print('create_policy non post')
        profile_id = ProfileModel.objects.get(
            id=get_profile_id(get_id_from_session(request)))
        
        proposal_no = request.POST['proposal_no']
        policy_no = request.POST['policy_no']
        customer_name = request.POST['customer_name']
        insurance_company = request.POST['insurance_company']
        sp_name = request.POST['sp_name']
        sp_brokercode = request.POST['sp_brokercode']
        product_name = request.POST['product_name']        
        policy_type = request.POST['policy_type']
        risk_start_date = request.POST['risk_start_date']
        risk_end_date = request.POST['risk_end_date']
        issue_date = request.POST['issue_date']
        policy_term = request.POST['policy_term']
        bqp = request.POST['bqp']
        pos = request.POST['pos']
        cpa = request.POST['cpa']
        employee = request.POST['employee']
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
        Policy.objects.create(profile_id=profile_id, proposal_no=proposal_no, policy_no=policy_no, customer_name=customer_name, 
                              insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                              product_name=product_name, policy_type=policy_type,  
                              risk_start_date=risk_start_date,
                              risk_end_date=risk_end_date, issue_date=issue_date,  
                              policy_term=policy_term,  bqp=bqp, pos=pos, cpa=cpa,
                              employee=employee, proposal=proposal, mandate=mandate,
                              policy=policy, previous_policy=previous_policy, pan_card=pan_card, aadhar_card=aadhar_card, inspection_report=inspection_report,
                              OD_premium=OD_premium,  TP_terrorism=TP_terrorism, net=net, gst_amount=gst_amount,total=total,
                              payment_mode=payment_mode)

        data = Policy.objects.filter(profile_id=get_profile_id(
            get_id_from_session(request))).order_by('-policyid').values()
        return render(request, 'policylist/policy_entry_list.html', {'data': data})


def apply_policy(request, id):
    try:
        print('apply_policy')

        data = Policy.objects.get(policyid=id)
        print(data)
        
        if data.vehicle_catagory == 'TWO WHEELER':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(cubic_capacity__contains=data.cubic_capacity) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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

        elif data.vehicle_catagory == 'PRIVATE CAR':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(cubic_capacity__contains=data.cubic_capacity) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(gvw__contains=data.gvw) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(gvw__contains=data.gvw) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(cubic_capacity__contains=data.cubic_capacity) &
                                           Q(seating_capacity__contains=data.seating_capacity) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                cap = int(data.seating_capacity)
                print('cap ', cap)

                if cap < 5:
                    cap = 'BELOW 5'
                elif cap > 4 and cap < 8:
                    cap = '5-7'
                elif cap > 6 and cap < 13:
                    cap = '7-12'
                elif cap > 11 and cap < 19:
                    cap = '12-18'
                else:
                    cap = 'ABOVE 18'

                print('cap ', cap)
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(seating_capacity__contains=cap) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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

        elif data.vehicle_catagory == 'SCHOOL BUS-SCHOOL NAME':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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

        elif data.vehicle_catagory == 'SCHOOL BUS-INDIVIDUAL NAME':
            try:
                reg = data.registration_no[0:4]
                data1 = Payout.objects.get(Q(insurance_company__contains=data.insurance_company) &
                                           Q(sp_name__contains=data.sp_name) &
                                           Q(sp_brokercode__contains=data.sp_brokercode) &
                                           Q(rto_city__contains=reg) &
                                           Q(vehicle_makeby__contains=data.vehicle_makeby) &
                                           Q(vehicle_model__contains=data.vehicle_model) &
                                           Q(vehicle_catagory__contains=data.vehicle_catagory) &
                                           Q(vehicle_fuel_type__contains=data.vehicle_fuel_type) &
                                           Q(mfg_year__contains=data.mfg_year) &
                                           Q(addon__contains=data.addon) &
                                           Q(ncb__contains=data.ncb) &
                                           Q(coverage_type__contains=data.coverage_type) &
                                           Q(policy_type__contains=data.policy_type) &
                                           Q(policy_term__contains=data.policy_term) &
                                           Q(cpa__contains=data.cpa)
                                           )
                print('payout data ', data1)
                # Agent payout
                agent_od_reward = data1.agent_od_reward
                agent_od_amount = (data.OD_premium * agent_od_reward) / 100
                agent_tp_reward = data1.agent_tp_reward
                agent_tp_amount = (data.TP_terrorism * agent_tp_reward) / 100
                # Self payout
                self_od_reward = data1.self_od_reward
                self_od_amount = (data.OD_premium * self_od_reward) / 100
                self_tp_reward = data1.self_tp_reward
                self_tp_amount = (data.TP_terrorism * self_tp_reward) / 100

                print('payout data ', agent_od_reward)
                print('payout data ', agent_od_amount)
                print('payout data ', agent_tp_reward)
                print('payout data ', agent_tp_amount)

                print('payout data ', agent_od_reward)

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
       
        return redirect('bima_policy:create_policy')
    except Exception as ex:
        print(ex)
        return HttpResponse(ex)


def policy_entry(request):
    print('policy_entry method')

    data = Policy.objects.filter(profile_id=get_profile_id(get_id_from_session(
        request))).order_by('-policyid').filter(Q(issue_date=datetime.now().date())).values()

    datag = Agents.objects.filter(
        profile_id=get_profile_id(get_id_from_session(request)))

    paginator = Paginator(data, per_page=25)
    try:
        data = paginator.get_page(request.GET.get('page'))
        return render(request, 'policylist/policy_entry_list.html', {'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as ex:
        page_obj = paginator.get_page(request.GET.get(paginator.num_pages))
        print(ex)
        return render(request, 'policylist/policy_entry_list.html', {'select_length': '25', 'period': 'TODAY', 'data': data, 'datag': datag, 'is_user': is_user(request)})


def policy_entry_filter(request, value1, value2, period, select_length):
    print('policy_entry_filter method')
    print(select_length)

    value1 = value1.replace("*", "-")
    value2 = value2.replace("*", "-")

    value1 = value1.split('-')
    value2 = value2.split('-')

    value1 = datetime(int(value1[2]), int(value1[1]), int(value1[0]))
    value2 = datetime(int(value2[2]), int(value2[1]), int(value2[0]))

    data = Policy.objects.filter(profile_id=get_profile_id(get_id_from_session(
        request))).order_by('-policyid').filter(Q(issue_date__gte=value1) & Q(issue_date__lte=value2)).values()

    datag = Agents.objects.filter(
        profile_id=get_profile_id(get_id_from_session(request)))

    paginator = Paginator(data, per_page=select_length)
    try:
        data = paginator.get_page(request.GET.get('page'))
        return render(request, 'policylist/policy_entry_list.html', {'select_length': select_length, 'period': period, 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as ex:
        page_obj = paginator.get_page(request.GET.get(paginator.num_pages))
        print(ex)
        return render(request, 'policylist/policy_entry_list.html', {'select_length': select_length, 'period': period, 'data': data, 'datag': datag, 'is_user': is_user(request)})


def policy_entry_filter_nopayout(request, value1, value2, period, select_length, payout):
    print('policy_entry_filter_nopayout method')
    print(payout)

    value1 = value1.replace("*", "-")
    value2 = value2.replace("*", "-")

    value1 = value1.split('-')
    value2 = value2.split('-')

    value1 = datetime(int(value1[2]), int(value1[1]), int(value1[0]))
    value2 = datetime(int(value2[2]), int(value2[1]), int(value2[0]))

    data = Policy.objects.filter(profile_id=get_profile_id(get_id_from_session(
        request))).order_by('-policyid').filter(Q(issue_date__gte=value1) & Q(issue_date__lte=value2) & Q(agent_od_reward__isnull=True)).values()

    datag = Agents.objects.filter(
        profile_id=get_profile_id(get_id_from_session(request)))

    paginator = Paginator(data, per_page=25)
    try:
        data = paginator.get_page(request.GET.get('page'))
        return render(request, 'policylist/policy_entry_list.html', {'select_length': select_length, 'period': period,  'payout': payout, 'data': data, 'datag': datag, 'is_user': is_user(request)})
    except Exception as ex:
        page_obj = paginator.get_page(request.GET.get(paginator.num_pages))
        print(ex)
        return render(request, 'policylist/policy_entry_list.html', {'select_length': select_length, 'period': period, 'payout': payout, 'data': data, 'datag': datag, 'is_user': is_user(request)})


def policy_entrydata(request, id):
    print('policy_entrydata')
    if request.method == "POST":
        print('policy_entrydata post')
        
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
        cpa = request.POST['cpa']
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
        employee = request.POST['employee']
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
                    gst_gcv_amount=gst_gcv_amount,  total=total )
        
        
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

        return redirect('bima_policy:policy_entry')
    else:
        print('get entrydata', id)
        print(is_user(request))

        data = Policy.objects.get(policyid=id)
        data_sp = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))

        data_ins = InsuranceCompany.objects.filter(
            profile_id=get_id_from_session(request))
        data_vmb = VehicleMakeBy.objects.filter(
            profile_id=get_id_from_session(request))
        data_vm = VehicleModelName.objects.filter(
            profile_id=get_id_from_session(request))
        data_vc = VehicleCategory.objects.filter(
            profile_id=get_id_from_session(request))
        data_ct = CoverageType.objects.filter(
            profile_id=get_id_from_session(request))
        data_bqp = BQP.objects.filter(
            profile_id=get_id_from_session(request))
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
        return render(request, 'policylist/edit_policy.html', {'is_user': is_user(request), 'is_motor_form': is_motor_form, 'data': data, 'data_sp': data_sp, 'data_ins': data_ins, 'data_vmb': data_vmb, 'data_vm': data_vm, 'data_vc': data_vc, 'data_ct': data_ct, 'data_bqp': data_bqp})


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
        datag = Agents.objects.filter(profile_id=get_id_from_session(request))
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


def policy_deleteo(request, id):
    if request.method == 'GET':
        Policy.objects.get(policyid=id).delete()
        return redirect('bima_policy:policy_entry')


def policy_delete(request, id):
    print('policy_delete')

    try:
        if id.__contains__("|"):
            arrays = id.split("|")
            for i in arrays:
                Policy.objects.filter(policy_no=i).delete()
                print('Deleted: ', i)
    except Exception as ex:
        print(ex)

    if request.method == 'GET':
        # Policy.objects.get(policyid=id).delete()
        return redirect('bima_policy:policy_entry')


def logout(request):
    request.session.clear()
    return render(request, 'login.html')


def agent(request):
    print('agent method')
    # data = Agents.objects.filter(profile_id=get_id_from_session(request))
    data = Agents.objects.all()

    print(data)
    return render(request, 'agents/agent.html', {'data': data})


def add_agent(request):
    try:
        if request.method == "GET":
            Adata = Slab.objects.filter(
                profile_id=get_id_from_session(request))
            data = Agents.objects.filter(
                profile_id=get_id_from_session(request))

            return render(request, 'agents/add_agent.html', {'data': data, 'Adata': Adata})
    except Agents.DoesNotExist:
        return render(request, 'agents/add_agent.html')
    else:
        if 'subagent' in request.POST:
            data = ProfileModel.objects.get(id=get_id_from_session(request))
            full_name = request.POST['full_name']
            email_id = request.POST['email_id']
            phone = request.POST['phone']
            address = request.POST['address']
            state = request.POST['state']
            city = request.POST['city']
            agent_slab = request.POST['agent_slab']
            gstin = request.POST['gstin']
            pan = request.POST['pan']
            aadhar_no = request.POST['aadhar_no']
            rural_urban = request.POST['rural_urban']
            docs = request.POST.get('docs')
            password = request.POST['password']
            # a=Agents.objects.get(full_name=full_name)
            # if full_name==Agents.objects.get(full_name=a.full_name):
            #     error_message="Full Name already exist! Please enter unique name to continue..."
            #     return redirect('bima_policy:add_agent',{'error_message':error_message})
            # else:
            Agents.objects.create(full_name=full_name, email_id=email_id, mob_no=phone, address=address, state=state,
                                  city=city, slab=agent_slab, GSTIN=gstin, PAN=pan,  aadhar_no=aadhar_no,  rural_urban=rural_urban,
                                  document=docs, password=password, profile_id=data)
            return redirect('bima_policy:agent')


# PayoutView
def slab(request):
    if request.method == "GET":
        try:
            data = Slab.objects.filter(profile_id=get_id_from_session(request))
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
    print('slab_payout')
    if request.method == 'GET':
        try:
            data = Payout.objects.filter(
                profile_id=get_id_from_session(request))
            data1 = data.filter(slab_name=id)
            return render(request, 'payout/slab_payoutlist.html', {'data1': data1})
        except Payout.DoesNotExist:
            return render(request, 'payout/slab_payoutlist.html')


def slab_payoutform(request):
    print('slab_payoutform')

    if request.method == "GET":
        print('slab_payoutform get')
        data_sp = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))
        data_bc = BrokerCode.objects.filter(
            profile_id=get_id_from_session(request))
        data_ins = InsuranceCompany.objects.filter(
            profile_id=get_id_from_session(request))
        data_vmb = VehicleMakeBy.objects.filter(
            profile_id=get_id_from_session(request))
        data_vm = VehicleModelName.objects.filter(
            profile_id=get_id_from_session(request))
        data_vc = VehicleCategory.objects.filter(
            profile_id=get_id_from_session(request))
        data_ct = CoverageType.objects.filter(
            profile_id=get_id_from_session(request))
        slab = Slab.objects.filter(profile_id=get_id_from_session(request))

        # print(state_rto.rto_id)
        print(data_bc)
        return render(request, 'payout/slab_payoutform.html', {'slab': slab, 'data_sp': data_sp, 'data_bc': data_bc,'data_ins': data_ins, 'data_vmb': data_vmb, 'data_vm': data_vm, 'data_vc': data_vc, 'data_ct': data_ct})

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

        product_name = ','.join(product_name)
        insurance_company = ','.join(insurance_company)
        sp_name = ','.join(sp_name)
        sp_brokercode = ','.join(sp_brokercode)
        vehicle_makeby = ','.join(vehicle_makeby)
        vehicle_model = ','.join(vehicle_model)
        vehicle_catagory = ','.join(vehicle_catagory)
        vehicle_fuel_type = ','.join(vehicle_fuel_type)
        mfg_year = ','.join(mfg_year)
        rto_city = ','.join(rto)
        addon = ','.join(addon)
        ncb = ','.join(ncb)
        gvw = ','.join(gvw)
        cubic_capacity = ','.join(cubic_capacity)
        seating_capacity = ','.join(seating_capacity)
        coverage_type = ','.join(coverage_type)
        policy_type = ','.join(policy_type)
        cpa = ','.join(cpa)
        policy_term = ','.join(policy_term)

        print(product_name)

        # my_list = product_names.split(",")
        # print( my_list)
        Payout.objects.create(payout_name=payout_name, slab_name=s, product_name=product_name, 
                              insurance_company=insurance_company, sp_name=sp_name,  sp_brokercode=sp_brokercode,
                              vehicle_makeby=vehicle_makeby, vehicle_model=vehicle_model,
                              vehicle_catagory=vehicle_catagory, vehicle_fuel_type=vehicle_fuel_type, mfg_year=mfg_year,
                              rto_city=rto_city, addon=addon, ncb=ncb, gvw=gvw, cubic_capacity=cubic_capacity, seating_capacity=seating_capacity,
                              coverage_type=coverage_type, policy_type=policy_type, cpa=cpa, policy_term=policy_term,
                              agent_od_reward=agent_od_reward,
                              agent_tp_reward=agent_tp_reward,
                              self_od_reward=self_od_reward,
                              self_tp_reward=self_tp_reward,
                              profile_id=data)
        print("insert data")
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

        product_name = ','.join(product_name)
        insurance_company = ','.join(insurance_company)
        sp_name = ','.join(sp_name)
        sp_brokercode = ','.join(sp_brokercode)
        vehicle_makeby = ','.join(vehicle_makeby)
        vehicle_model = ','.join(vehicle_model)
        vehicle_catagory = ','.join(vehicle_catagory)
        vehicle_fuel_type = ','.join(vehicle_fuel_type)
        mfg_year = ','.join(mfg_year)
        rto_city = ','.join(rto)
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
        print("done")
        return redirect('bima_policy:slab')

    else:
        data = Payout.objects.get(payoutid=id)
        data_sp = ServiceProvider.objects.filter(
            profile_id=get_id_from_session(request))
        data_bc = BrokerCode.objects.filter(
            profile_id=get_id_from_session(request))
        
        data_ins = InsuranceCompany.objects.filter(
            profile_id=get_id_from_session(request))
        data_vmb = VehicleMakeBy.objects.filter(
            profile_id=get_id_from_session(request))
        data_vm = VehicleModelName.objects.filter(
            profile_id=get_id_from_session(request))
        data_vc = VehicleCategory.objects.filter(
            profile_id=get_id_from_session(request))
        data_ct = CoverageType.objects.filter(
            profile_id=get_id_from_session(request))

        slab = Slab.objects.filter(profile_id=get_id_from_session(request))

        return render(request, 'payout/edit_payoutform.html', {'data': data, 'slab': slab, 'data_sp': data_sp, 'data_bc': data_bc,'data_ins': data_ins, 'data_vmb': data_vmb, 'data_vm': data_vm, 'data_vc': data_vc, 'data_ct': data_ct})


def payout_delete(request, id):
    Payout.objects.filter(payoutid=id).delete()
    return redirect('bima_policy:slab')


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
    agent_obj = Agents.objects.filter(profile_id=get_id_from_session(request))
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
    agent_obj = Agents.objects.filter(profile_id=get_id_from_session(request))
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
