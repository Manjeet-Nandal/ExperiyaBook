from enum import unique
import uuid
from django.forms import DateTimeField
from djongo import models

# Create your models here.


class ProfileModel(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:15].upper(), editable=False, max_length=30)
    full_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=30)
    mob_no = models.CharField(max_length=10)
    state = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=30)
    password = models.CharField(max_length=20)
    package_GB = models.CharField(max_length=10)
    package_MB = models.CharField(max_length=10)
    package_duration = models.CharField(max_length=10)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        self.login_id = uuid.uuid4().hex[:10].upper()
        super(ProfileModel, self).save(*args, **kwargs)


class StaffModel(models.Model):
    login_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:10].upper(), editable=False, max_length=10)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    staffname = models.CharField(max_length=100)
    password = models.CharField(max_length=20)
    status = models.CharField(default='Active', max_length=20)
    # reload UUID after inserting data

    def save(self, *args, **kwargs):
        self.login_id = uuid.uuid4().hex[:10].upper()
        super(StaffModel, self).save(*args, **kwargs)


class BankDetail(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    beneficiary_name = models.CharField(max_length=50)
    acc_no = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=50)
    # reload UUID after inserting data

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(BankDetail, self).save(*args, **kwargs)


class RtoConversionModel(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    rto_series = models.CharField(max_length=10)
    rto_return = models.CharField(max_length=10)
    status = models.CharField(default='Active', max_length=20)

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(RtoConversionModel, self).save(*args, **kwargs)


class InsuranceCompany(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    comp_name = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.comp_name

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(InsuranceCompany, self).save(*args, **kwargs)


class Agents(models.Model):
    login_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:10].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=20)
    mob_no = models.CharField(max_length=12)
    email_id = models.EmailField(max_length=30)
    address = models.CharField(max_length=100)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    slab = models.CharField(max_length=100)
    GSTIN = models.CharField(max_length=100)
    PAN = models.CharField(max_length=100)
    aadhar_no = models.CharField(max_length=100)
    rural_urban = models.CharField(max_length=100)
    document = models.FileField()
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.login_id = uuid.uuid4().hex[:10].upper()
        super(Agents, self).save(*args, **kwargs)


class ServiceProvider(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    mob_no = models.IntegerField()
    email_id = models.EmailField(max_length=30)
    address = models.CharField(max_length=100)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    GSTIN = models.CharField(max_length=100)
    PAN = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(ServiceProvider, self).save(*args, **kwargs)


class BrokerCode(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(BrokerCode, self).save(*args, **kwargs)


class Slab(models.Model):
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    slab_name = models.CharField(primary_key=True, unique=True, max_length=30)
    status = models.CharField(default='Active', max_length=10)

    def __str__(self):
        return self.slab_name


class Payout(models.Model):
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    payoutid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:7].upper(), editable=False, max_length=7)
    slab_name = models.ForeignKey(Slab, on_delete=models.CASCADE)
    payout_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    insurer = models.CharField(max_length=255)
    sp_name = models.CharField(max_length=255)
    vehicle_makeby = models.CharField(max_length=255)
    vehicle_model = models.CharField(max_length=255)
    vehicle_catagory = models.CharField(max_length=255)
    vehicle_fuel_type = models.CharField(max_length=255)
    mfg_year = models.CharField(max_length=255)
    
    rto_city = models.CharField(max_length=1000)

    addon = models.CharField(max_length=50)
    ncb = models.CharField(max_length=50)
    gvw = models.CharField(max_length=100)
    cubic_capacity = models.CharField(max_length=100)
    seating_capacity = models.CharField(max_length=100)
    coverage_type = models.CharField(max_length=100)
    case_type = models.CharField(max_length=50)
    cpa = models.CharField(max_length=50)
    policy_term = models.CharField(max_length=50)    

    agent_od_reward = models.IntegerField(max_length=50)
    agent_tp_reward = models.IntegerField(max_length=50)

    self_od_reward = models.IntegerField(max_length=50)
    self_tp_reward = models.IntegerField(max_length=50)

    def __str__(self):
        return self.payout_name

    def save(self, *args, **kwargs):
        self.payoutid = uuid.uuid4().hex[:7].upper()
        super(Payout, self).save(*args, **kwargs)


class VehicleMakeBy(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.company

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(VehicleMakeBy, self).save(*args, **kwargs)


class VehicleModelName(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.model

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(VehicleModelName, self).save(*args, **kwargs)


class VehicleCategory(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.category

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(VehicleCategory, self).save(*args, **kwargs)


class Policy(models.Model):
    policyid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:7].upper(), editable=False, max_length=7)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    proposal_no = models.CharField(max_length=50, unique=True)
    policy_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    insurance_company = models.CharField(max_length=100)
    sp_name = models.CharField(max_length=100)
    sp_brokercode = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100, blank=True)
    registration_no = models.CharField(max_length=50, blank=True)
    rto_state = models.CharField(max_length=100, blank=True)
    rto_city = models.CharField(max_length=1000, blank=True)
    vehicle_makeby = models.CharField(max_length=100, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_catagory = models.CharField(max_length=50, blank=True)
    vehicle_fuel_type = models.CharField(max_length=50, blank=True)
    mfg_year = models.IntegerField(blank=True)
    addon = models.CharField(max_length=50, blank=True)
    ncb = models.CharField(max_length=50, blank=True)
    cubic_capacity = models.CharField(max_length=50, blank=True)
    gvw = models.CharField(max_length=50, blank=True)
    seating_capacity = models.CharField(max_length=50, blank=True)
    coverage_type = models.CharField(max_length=100, blank=True)
    policy_type = models.CharField(max_length=100)
    cpa = models.CharField(max_length=100)
    risk_start_date = models.DateField()
    risk_end_date = models.DateField()
    issue_date = models.DateField()
    insured_age = models.IntegerField()
    policy_term = models.IntegerField()
    payment_mode = models.CharField(max_length=100)
    bqp = models.CharField(max_length=100)
    pos = models.CharField(max_length=100)
    employee = models.CharField(max_length=100)
    OD_premium = models.IntegerField()
    TP_terrorism = models.IntegerField()
    net = models.IntegerField()
    gst_amount = models.IntegerField()
    gst_gcv_amount = models.IntegerField(blank=True)   
    total = models.IntegerField()
    agent_od_reward = models.IntegerField(blank=True)
    agent_od_amount = models.IntegerField(blank=True)
    agent_tp_reward = models.IntegerField(blank=True)
    agent_tp_amount = models.IntegerField(blank=True)
    self_od_reward = models.IntegerField(blank=True)
    self_od_amount = models.IntegerField(blank=True)
    self_tp_reward = models.IntegerField(blank=True)
    self_tp_amount = models.IntegerField(blank=True)
    proposal = models.FileField(upload_to='media/documents/')
    mandate = models.FileField(upload_to='media/documents/')
    policy = models.FileField(upload_to='media/documents/')
    previous_policy = models.FileField(upload_to='media/documents/', null=True)
    pan_card = models.FileField(upload_to='media/documents/')
    aadhar_card = models.FileField(upload_to='media/documents/')
    vehicle_rc = models.FileField(upload_to='media/documents/')
    inspection_report = models.FileField(upload_to='media/documents/')

    def __str__(self):
        return self.customer_name

    def save(self, *args, **kwargs):
        self.policyid = uuid.uuid4().hex[:7].upper()
        super(Policy, self).save(*args, **kwargs)


class PolicyNonMotor(models.Model):
    policyid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:7].upper(), editable=False, max_length=7)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    proposal_no = models.CharField(max_length=50, unique=True)
    policy_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    insurance_company = models.CharField(max_length=100)
    sp_name = models.CharField(max_length=100)
    sp_brokercode = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    registration_no = models.CharField(max_length=50)
    coverage_type = models.CharField(max_length=100)
    case_type = models.CharField(max_length=100)
    risk_start_date = models.DateField()
    risk_end_date = models.DateField()
    issue_date = models.DateField()
    insured_age = models.IntegerField()
    policy_term = models.IntegerField()
    payment_mode = models.CharField(max_length=100)
    bqp = models.CharField(max_length=100)
    pos = models.CharField(max_length=100)
    employee = models.CharField(max_length=100)
    OD_premium = models.IntegerField()
    TP_premium = models.IntegerField()
    TP_terrorism = models.IntegerField()
    net = models.IntegerField()
    GST = models.IntegerField()
    total = models.IntegerField()
    proposal = models.FileField(upload_to='media/documents/')
    mandate = models.FileField(upload_to='media/documents/')
    policy = models.FileField(upload_to='media/documents/')
    previous_policy = models.FileField(upload_to='media/documents/', null=True)
    pan_card = models.FileField(upload_to='media/documents/')
    aadhar_card = models.FileField(upload_to='media/documents/')
    inspection_report = models.FileField(upload_to='media/documents/')

    def __str__(self):
        return self.customer_name

    def save(self, *args, **kwargs):
        self.policyid = uuid.uuid4().hex[:7].upper()
        super(PolicyNonMotor, self).save(*args, **kwargs)


class InsuranceUpload(models.Model):
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    policyid = models.OneToOneField(Policy, verbose_name=(
        'policyid'), primary_key=True, on_delete=models.CASCADE)
    ins_upload = models.FileField(upload_to='media/documents/')


class UserRole(models.Model):
    user_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:15].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(
        ProfileModel, blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        Agents, null=True, blank=True, on_delete=models.CASCADE)
    staf = models.ForeignKey(StaffModel, null=True,
                             blank=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='user')


class States(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.state

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(States, self).save(*args, **kwargs)


class StateRtos(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.state

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(StateRtos, self).save(*args, **kwargs)


class rtotables(models.Model):
    sid_id = models.ForeignKey(StateRtos, on_delete=models.CASCADE)
    rto_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:5].upper(), editable=False, max_length=5)
    RegNo = models.CharField(max_length=200)

    def __str__(self):
        return self.RegNo

    def save(self, *args, **kwargs):
        # self.payoutid = uuid.uuid4().hex[:5].upper()
        self.id = uuid.uuid4().hex[:6].upper()
        super(rtotables, self).save(*args, **kwargs)


class BQP(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(BQP, self).save(*args, **kwargs)


class CoverageType(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(CoverageType, self).save(*args, **kwargs)
