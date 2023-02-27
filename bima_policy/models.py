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
    ('HDFC Ergo', 'HDFC Ergo'),
    ('ICICI Lombard', 'ICICI Lombard'),
    ('BAJAJ Allianz', 'BAJAJ Allianz'),
    ('IFFCO Tokio', 'IFFCO Tokio'),
    ('TATA AIG', 'TATA AIG'),
    ('Royal Sundram', 'Royal Sundram'),
    ('United India Ins', 'United India Ins'),
    ('Future Generali', 'Future Generali'),
    ('Go digit', 'Go digit'),
    ('Shri Ram', 'Shri Ram'),
    ('SBI General Ins', 'SBI General Ins'),
    ('Kotak General Ins', 'Kotak General Ins'),
    ('Reliance', 'Reliance'),
    ('Magma Gen Ins', 'Magma Gen Ins'),
    ('THE NEW INDIA ASSURANCE', 'THE NEW INDIA ASSURANCE')
)

product_name = (
    ('Motor', 'Motor'),
    ('Fire', 'Fire'),
    ('Marine', 'Marine'),
    ('Burgulary', 'Burgulary'),
    ('Shopkeeper', 'Shopkeeper'),
    ('Engineering', 'Engineering'),
    ('WC', 'WC'),
    ('Others', 'Others')
)

product_type = (
    ('Private Car', 'Private Car'),
    ('Commercial Vehicle', 'Commercial Vehicle'),
    ('GCV-3W', 'GCV-3W'),
    ('GCV-4W', 'GCV-4W'),
    ('GCV-Erickshaw', 'GCV-Erickshaw'),
    ('Kisan Tractor', 'Kisan Tractor'),
    ('Misc-D', 'Misc-D'),
    ('PCV-3W', 'PCV-3W'),
    ('PCV-Bus and Maxi', 'PCV-Bus and Maxi'),
    ('PCV-Erickshaw', 'PCV-Erickshaw'),
    ('PCV-School Bus', 'PCV-School Bus'),
    ('PCV-Taxi 4W', 'PCV-Taxi 4W'),
    ('TW Bike', 'TW Bike'),
    ('TW Scooter', 'TW Scooter'),
    ('Two Wheeler', 'Two Wheeler')
)

yes_no = (
    ('No', 'No'),
    ('Yes', 'Yes')
)

fuel = (
    ('CNG', 'CNG'),
    ('Diesel', 'Diesel'),
    ('Electric', 'Electric'),
    ('Petrol', 'Petrol'),
    ('Petrol/CNG', 'Petrol/CNG')
)

cubic_capacity = (
    ('Below 1000', 'Below 1000'),
    ('1000-1500', '1000-1500'),
    ('Above 1500', 'Above 1500')
)

gvw = (
    ('Below 2000', 'Below 2000'),
    ('2000-2500', '2000-2500'),
    ('2500-3500', '2500-3500'),
    ('3500-7000', '3500-7000'),
    ('7000-7500', '7000-7500'),
    ('7500-12000', '7500-12000'),
    ('12000-25000', '12000-25000'),
    ('25000-40000', '25000-40000'),
    ('Above 40000', 'Above 40000')
)

seating_capacity = (
    ('Below 5', 'Below 5'),
    ('5-7', '5-7'),
    ('7-12', '7-12'),
    ('12-18', '12-18'),
    ('Above 18', 'Above 18')
)

coverage_type = (
    ('1+2 Pvt Car', '1+2 Pvt Car'),
    ('1+4 Two Wheeler', '1+4 Two Wheeler'),
    ('TP Only', 'TP Only'),
    ('OD Only', 'OD Only'),
    ('Standard Policy', 'Standard Policy'),
    ('Comprehensive Package Policy', 'Comprehensive Package Policy'),
    ('Others', 'Others')
)

types = (
    ('Fresh', 'Fresh'),
    ('Renewal', 'Renewal'),
    ('Rollover', 'Rollover'),
    ('Endorsement', 'Endorsement')
)

rto_state = (
    ('sonipat', 'Fresh'),
    ('Renewal', 'Renewal'),
    ('Rollover', 'Rollover'),
    ('Endorsement', 'Endorsement')
)

mfg_year = (
    ('2030', '2030'),
    ('2029', '2029'),
    ('2028', '2028'),
    ('2027', '2027'),
    ('2026', '2026'),
    ('2025', '2025'),
    ('2024', '2024'),
    ('2023', '2023'),
    ('2022', '2022'),
    ('2021', '2021'),
    ('2020', '2020'),
    ('2019', '2019'),
    ('2018', '2018'),
    ('2017', '2017'),
    ('2016', '2016'),
    ('2015', '2015'),
    ('2014', '2014'),
    ('2013', '2013'),
    ('2012', '2012'),
    ('2011', '2011'),
    ('2010', '2010'),
    ('2009', '2009'),
    ('2008', '2008'),
    ('2007', '2007'),
    ('2006', '2006'),
    ('2005', '2005'),
    ('2004', '2004'),
    ('2003', '2003'),
    ('2002', '2002'),
    ('2001', '2001')
)

payment_mode = (
    ('Customer Online', 'Customer Online'),
    ('Self Online', 'Self Online'),
    ('Cash', 'Cash'),
    ('Cut Pay', 'Cut Pay'),
    ('Customer Cheque', 'Customer Cheque'),
    ('Self Cheque', 'Self Cheque')
)


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


class PolicyOld(models.Model):
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
        max_length=50, choices=insurer_name, default='BAJAJ Allianz')
    location = models.CharField(max_length=100, default='NA', blank=True)
    product_name = models.CharField(
        max_length=50, choices=product_name, default='Motor')
    product_type = models.CharField(
        max_length=50, choices=product_type, default='Private Car')
    registration = models.CharField(max_length=50)
    rto_city = models.CharField(max_length=50)
    rto_state = models.CharField(max_length=50)
    vehicle_makeby = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    manu_year = models.CharField(max_length=50)
    addon = models.CharField(max_length=50, choices=yes_no, default='No')
    ncb = models.CharField(max_length=50, choices=yes_no, default='No')
    fuel_type = models.CharField(max_length=50)
    cubic_capacity = models.CharField(max_length=50)
    gvw = models.CharField(max_length=50)
    seating_capacity = models.CharField(max_length=50)
    coverage_type = models.CharField(max_length=50)
    case_type = models.CharField(max_length=50)
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
    bqp = models.CharField(max_length=100, default='NA')
    pos = models.CharField(max_length=100)
    employee = models.CharField(max_length=100)
    proposal = models.CharField(max_length=100, default='NA', blank=True)
    mandate = models.CharField(max_length=100, default='NA', blank=True)
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


class Policy(models.Model):
    policyid = models.CharField(primary_key=True, unique=True, default=uuid.uuid4(
    ).hex[:7].upper(), editable=False, max_length=7)
    # Agent=models.ForeignKey(Agents,on_delete=models.CASCADE)
    profile_id = models.ForeignKey(ProfileModel, on_delete=models.CASCADE)
    proposal_no = models.CharField(max_length=50, unique=True)
    policy_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    insurance_company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100)
    registration_no = models.CharField(max_length=50)
    rto_city = models.CharField(max_length=100)
    rto_state = models.CharField(max_length=100)
    vehicle_makeby = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_fuel_type = models.CharField(max_length=50)
    # vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE)
    mfg_year = models.IntegerField()
    addon = models.CharField(max_length=50)
    ncb = models.CharField(max_length=50)
    cubic_capacity = models.CharField(max_length=50)
    gvw = models.CharField(max_length=50)
    seating_capacity = models.CharField(max_length=50)
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
    proposal = models.CharField(max_length=100)
    mandate = models.CharField(max_length=100)
    OD_premium = models.IntegerField()
    TP_premium = models.IntegerField()
    TP_terrorism = models.IntegerField()
    net = models.IntegerField()
    GST = models.IntegerField()
    total = models.IntegerField()
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
        # self.payoutid = uuid.uuid4().hex[:10].upper()
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
        super(rtotables, self).save(*args, **kwargs)
