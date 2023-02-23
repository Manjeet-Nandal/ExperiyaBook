from enum import unique
import uuid
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
        return self.full_name

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


class ProductName(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    prod_name = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.prod_name

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(ProductName, self).save(*args, **kwargs)


class ProductType(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    # profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    prod_type = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

    def __str__(self):
        return self.prod_type

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(ProductType, self).save(*args, **kwargs)


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
    document = models.FileField()
    status = models.CharField(default='Active', max_length=20)

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

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4().hex[:6].upper()
        super(ServiceProvider, self).save(*args, **kwargs)


class BrokerCode(models.Model):
    id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:6].upper(), editable=False, max_length=30)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    status = models.CharField(default='Active', max_length=20)

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
    status = models.CharField(default='Active', max_length=10)
    vehicle_category = models.CharField(max_length=50)
    policy_provider = models.CharField(max_length=50)
    Insurance_company = models.CharField(max_length=50)
    vehicle_make_by = models.CharField(max_length=50)
    rto = models.CharField(max_length=50)
    case_type = models.CharField(max_length=100)
    coverage = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    cpa = models.CharField(max_length=50)
    rewards_on = models.CharField(max_length=50)
    rewards_age = models.IntegerField()
    self_rewards_on = models.CharField(max_length=50)
    self_rewards_age = models.IntegerField()

    def __str__(self):
        return self.payout_name

    def save(self, *args, **kwargs):
        self.payoutid = uuid.uuid4().hex[:7].upper()
        super(Payout, self).save(*args, **kwargs)


insurer_name = (
    ('1', 'HDFC Ergo'),
    ('2', 'ICICI Lombard'),
    ('3', 'BAJAJ Allianz'),
    ('4', 'IFFCO Tokio'),
    ('5', 'TATA AIG'),
    ('6', 'Royal Sundram'),
    ('7', 'United India Ins'),
    ('8', 'Future Generali'),
    ('9', 'Go digit'),
    ('10', 'Shri Ram'),
    ('11', 'SBI General Ins'),
    ('12', 'Kotak General Ins'),
    ('13', 'Reliance'),
    ('14', 'Magma Gen Ins'),
    ('15', 'THE NEW INDIA ASSURANCE')
)

product_name = (
    ('1', 'Motor'),
    ('2', 'Fire'),
    ('3', 'Marine'),
    ('4', 'Burgulary'),
    ('5', 'Shopkeeper'),
    ('6', 'Engineering'),
    ('7', 'WC'),
    ('8', 'Others')
)

# product_type = (
#     ('1', 'Private Car'),
#     ('2', 'Commercial Vehicle'),
#     ('3', 'GCV-3W'),
#     ('4', 'GCV-4W'),
#     ('5', 'GCV-Erickshaw'),
#     ('6', 'Kisan Tractor'),
#     ('7', 'Misc-D'),
#     ('8', 'PCV-3W'),
#     ('9', 'PCV-Bus and Maxi'),
#     ('10', 'PCV-Erickshaw'),
#     ('11', 'PCV-School Bus'),
#     ('12', 'PCV-Taxi 4W'),
#     ('13', 'TW Bike'),
#     ('14', 'TW Scooter'),
#     ('15', 'Two Wheeler')
# )

product_type1 = {
    'car': 'car',
    'bike': 'bike'
}

yes_no = (
    ('1', 'Yes'),
    ('2', 'No')
)

fuel_type = (
    ('1', 'CNG'),
    ('2', 'Diesel'),
    ('3', 'Electric'),
    ('4', 'Petrol'),
    ('5', 'Petrol/CNG')
)

cubic_capacity = (
    ('1', 'Below 1000'),
    ('2', '1000-1500'),
    ('3', 'Above 1500')
)

gvw = (
    ('1', 'Below 2000'),
    ('2', '2000-2500'),
    ('3', '2500-3500'),
    ('4', '3500-7000'),
    ('5', '7000-7500'),
    ('6', '7500-12000'),
    ('7', '12000-25000'),
    ('8', '25000-40000'),
    ('9', 'Above 40000')
)

seating_capacity = (
    ('1', 'Below 5'),
    ('2', '5-7'),
    ('3', '7-12'),
    ('4', '12-18'),
    ('5', 'Above 18')
)

coverage_type = (
    ('1', '1+2 Pvt Car'),
    ('2', '1+4 Two Wheeler'),
    ('3', 'TP Only'),
    ('4', 'OD Only'),
    ('5', 'Standard Policy'),
    ('6', 'Comprehensive Package Policy'),
    ('7', 'Others')
)

types = (
    ('1', 'Fresh'),
    ('2', 'Renewal'),
    ('3', 'Rollover'),
    ('4', 'Endorsement')
)


class Policy(models.Model):
    id = models.CharField(unique=True, default=uuid.uuid4(
    ).hex[:15].upper(), editable=False, max_length=30)
    policyid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:7].upper(), editable=False, max_length=7)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    # sr_no = models.CharField(max_length=50)
    proposal_no = models.CharField(max_length=50, unique=True)
    policy_no = models.CharField(max_length=50, unique=True)
    insured_name = models.CharField(max_length=100)
    insurer_name = models.CharField(
        max_length=50, choices=insurer_name, default='1')
    location = models.CharField(max_length=100, blank=True)
    product_name = models.CharField(
        max_length=50, choices=product_name, default='1')
    product_type = models.CharField(
        max_length=50, choices=ProductType.objects.all())
    registration_no = models.CharField(max_length=50)
    rto_city = models.CharField(max_length=50)
    rto_state = models.CharField(max_length=50)
    make = models.CharField(max_length=50)
    model_variant = models.CharField(max_length=50)
    mfg_year = models.IntegerField()
    addon = models.CharField(max_length=50, choices=yes_no, default='1')
    ncb = models.CharField(max_length=50, choices=yes_no, default='1')
    fuel = models.CharField(max_length=50, choices=fuel_type, default='1')
    cubic_capacity = models.CharField(
        max_length=50, choices=cubic_capacity, default='1')
    gvw = models.CharField(max_length=50, choices=gvw, default='1')
    seating_capicity = models.CharField(
        max_length=50, choices=seating_capacity, default='1')
    coverage_type = models.CharField(
        max_length=50, choices=coverage_type, default='1')
    types = models.CharField(max_length=50, choices=types, default='1')
    risk_start_date = models.DateField()
    risk_end_date = models.DateField()
    issue_date = models.DateField()
    TP_premium = models.IntegerField()
    net = models.IntegerField()
    OD_premium = models.IntegerField()
    tp_terrorism = models.CharField(max_length=50)
    insured_age = models.IntegerField()
    policy_term = models.CharField(max_length=50)
    payment_mode = models.CharField(max_length=100)
    bqp = models.CharField(max_length=100, blank=True)
    pos = models.CharField(max_length=100)
    employee = models.CharField(max_length=100)
    proposal = models.CharField(max_length=100, blank=True)
    mandate = models.CharField(max_length=100, blank=True)
    policy = models.FileField(upload_to='media/documents/')
    previous_policy = models.FileField(upload_to='media/documents/')
    pan_card = models.FileField(upload_to='media/documents/')
    aadhar_card = models.FileField(upload_to='media/documents/')
    rc = models.FileField(upload_to='media/documents/')
    inspection_report = models.FileField(
        upload_to='media/documents/', blank=True)

    def __str__(self):
        return self.insured_name

    def save(self, *args, **kwargs):
        self.policyid = uuid.uuid4().hex[:7].upper()
        super(Policy, self).save(*args, **kwargs)


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


class StateRtos(models.Model):
    stateid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:10].upper(), editable=False, max_length=10)
    state = models.CharField(max_length=200)

    def __str__(self):
        return self.state

    def save(self, *args, **kwargs):
        self.payoutid = uuid.uuid4().hex[:10].upper()
        super(StateRtos, self).save(*args, **kwargs)


class rtotables(models.Model):
    sid_id = models.ForeignKey(StateRtos, on_delete=models.CASCADE)
    rto_id = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:5].upper(), editable=False, max_length=5)
    RegNo = models.CharField(max_length=200)

    def __str__(self):
        return self.RegNo

    def save(self, *args, **kwargs):
        self.payoutid = uuid.uuid4().hex[:5].upper()
        super(rtotables, self).save(*args, **kwargs)
