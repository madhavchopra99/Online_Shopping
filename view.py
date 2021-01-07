from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import sqlite3
from django.contrib import messages
from hashlib import sha3_512, sha3_256, md5
import random
from django.core.paginator import Paginator
import mail
from django.views.decorators.csrf import csrf_exempt

adminlogin = ('staff', 'admin')


def hash_password(email, password):
    hash_email = md5(email.encode()).hexdigest()
    hash1_password = sha3_256(password.encode()).hexdigest()

    password2 = hash_email + hash1_password + hash_email

    hash2_password = sha3_512(password2.encode()).hexdigest()

    return hash2_password

# print(hash_password('madhav@gmail.com','welcome'))
def myadmin(request):
    if request.session.get('user_permission') in adminlogin:
        return redirect(adminhome)

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = hash_password(email, request.POST.get('password'))

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = f"select * from user"
        cr.execute(q)
        for i in cr.fetchall():
            if email == i[1] and password == i[2] and i[3] in adminlogin:
                request.session['user'] = i[0]
                request.session['user_permission'] = i[3]
                con.close()
                return redirect(adminhome)
        else:
            messages.add_message(request, messages.ERROR, 'Invalid password or email')

    return render(request, 'myadmin/login.html')


def adminhome(request):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)

    return render(request, 'myadmin/base.html')


def logout(request):
    del request.session['user'], request.session['user_permission']
    return redirect(myadmin)


def userlogout(request):
    del request.session['user'], request.session['user_permission']
    return redirect(home)


def addcategory(request):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    context = {}
    if request.POST:
        name = request.POST['name'].lower()
        description = request.POST['description'].lower()
        q = "select name from category"
        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        cr.execute(q)

        for i in cr.fetchall():
            if i[0] == name:
                messages.add_message(
                    request, messages.ERROR, 'Duplicate Category Name')
                con.close()
                return render(request, 'myadmin/addcategory.html', context)

        q = f"""insert into category values(NULL,"{name}","{description}")"""
        cr.execute(q)
        con.commit()
        con.close()
        messages.add_message(request, messages.SUCCESS,
                             'Category Added Successfully')

    return render(request, 'myadmin/addcategory.html', context)


def viewcategory(request):
    if not request.session.get('user_permission') in ('staff', 'admin'):
        return redirect(myadmin)

    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select id,name,description from category order by name"
    cr.execute(q)
    data = []

    for row in cr.fetchall():
        data.append({'id': row[0], 'name': row[1], 'description': row[2]})
    # data.sort(key=lambda x: x.get('name'))

    context['data'] = data
    con.close()

    return render(request, 'myadmin/viewcategory.html', context)


def deletecategory(request, id):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"delete from category where id={id}"
    cr.execute(q)
    q = f"delete from product where category_id={id}"
    cr.execute(q)
    con.commit()
    con.close()
    messages.add_message(request, messages.SUCCESS,
                         'Category Deleted Successfully')

    return redirect(viewcategory)


def updatecategory(request, id):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    if request.POST:
        name = request.POST.get('name').lower()
        description = request.POST.get('description').lower()
        pname = request.POST.get('pname').lower()
        q = f"select name from category"
        cr.execute(q)
        ans = cr.fetchall()
        ans.remove(tuple([pname]))

        for i in ans:
            if i[0] == name:
                messages.add_message(
                    request, messages.ERROR, 'Duplicate Category Name')
                return redirect(updatecategory, id)

        q = f"""update category set name="{name}", description="{description}" where id={id}"""
        cr.execute(q)
        con.commit()
        con.close()
        messages.add_message(request, messages.SUCCESS, 'Updated Successfully')

        return redirect(viewcategory)

    q = f"select name,description from category where id={id}"
    cr.execute(q)
    name, description = cr.fetchone()
    context['name'] = name
    context['description'] = description
    con.close()

    return render(request, 'myadmin/updatecategory.html', context)


def addproduct(request):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    if request.POST:
        name = request.POST.get('name').lower()
        price = request.POST.get('price')
        priceafterdiscount = request.POST.get('priceAfterdiscount')
        try:
            assert float(price) >= float(
                priceafterdiscount), 'discount value greater than price'
        except AssertionError:
            messages.add_message(request, messages.ERROR, 'Invalid Pricing')
            return render(request, 'myadmin/addproduct.html', context)

        description = request.POST.get('description').lower()
        brand = request.POST.get('brand').lower()
        category = request.POST.get('category')
        photo = request.FILES.get('photo')
        fs = FileSystemStorage()
        filename = fs.save('product images/' + photo.name, photo)
        fileurl = fs.url(filename)
        q = f"""insert into product values (NULL ,"{name}",{price},{priceafterdiscount},"{description}","{brand}",{category},"{fileurl}")"""
        cr.execute(q)
        con.commit()
        messages.add_message(request, messages.SUCCESS,
                             'Product Added Successfully')

    q = "select id,name from category"
    cr.execute(q)
    category = []
    for i in cr.fetchall():
        category.append({'id': i[0], 'name': i[1]})
    context['category'] = category
    con.close()
    return render(request, 'myadmin/addproduct.html', context)


def viewproduct(request):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = "select id,name from category"
    cr.execute(q)
    category = {}

    for i in cr.fetchall():
        category[i[0]] = i[1]

    q = "select * from product order by name"
    cr.execute(q)
    data = []
    for i in cr.fetchall():
        data.append({'id': i[0], 'name': i[1], 'price': i[2], 'priceafter': i[3], 'description': i[4],
                     'brand': i[5], 'category': category[i[6]], 'photo': i[7]})

    context['data'] = data
    con.close()
    return render(request, 'myadmin/viewproduct.html', context)


def deleteproduct(request, id):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"delete from product where id={id}"
    cr.execute(q)
    con.commit()
    messages.add_message(request, messages.SUCCESS, 'Product Deleted')

    con.close()
    return redirect(viewproduct)


def updateproduct(request, id):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    if request.POST:
        name = request.POST.get('name').lower()
        price = request.POST.get('price')
        priceafterdiscount = request.POST.get('priceAfterdiscount')
        try:
            assert float(price) >= float(
                priceafterdiscount), 'discount value greater than price'
        except AssertionError:
            messages.add_message(request, messages.ERROR, 'Invalid Pricing')
            con.close()
            return redirect(updateproduct, id)

        description = request.POST.get('description').lower()
        brand = request.POST.get('brand').lower()
        category = request.POST.get('category')
        photo = request.FILES.get('photo')
        if photo:
            fs = FileSystemStorage()
            filename = fs.save('product images/' + photo.name, photo)
            fileurl = fs.url(filename)
            q = f"""update product set name="{name}", price={price}, priceAfterdiscount=
                {priceafterdiscount},description="{description}",brand="{brand}",
                category_id={category},photo = "{fileurl}" where id={id}"""
            cr.execute(q)
            con.commit()
            messages.add_message(request, messages.SUCCESS,
                                 'Product Updated Successfully')
            con.close()

            return redirect(viewproduct)

        else:
            q = f"""update product set name="{name}", price={price}, priceAfterdiscount=
                {priceafterdiscount},description="{description}",brand="{brand}",
                category_id={category} where id={id}"""
            cr.execute(q)
            con.commit()
            messages.add_message(request, messages.SUCCESS,
                                 'Product Updated Successfully')
            con.close()

            return redirect(viewproduct)

    q = f"select * from product where id = {id}"
    cr.execute(q)
    context['data'] = cr.fetchone()

    q = "select id,name from category"
    cr.execute(q)
    category = []
    for i in cr.fetchall():
        category.append({'id': i[0], 'name': i[1]})
    context['category'] = category
    con.close()

    return render(request, 'myadmin/updateproduct.html', context)


def users(request):
    context = {}
    if not request.session.get('user_permission') == 'admin':
        return redirect(myadmin)

    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()

    if request.POST:
        email = request.POST.get('email')
        permission = request.POST.get('permission')
        q = f"update user set permission='{permission}' where email='{email}'"
        cr.execute(q)
        con.commit()

    q = f"select name,email,permission from user order by name"
    cr.execute(q)
    data = []

    for i in cr.fetchall():
        data.append({'name': i[0], 'email': i[1], 'permission': i[2]})

    context['data'] = data
    con.close()

    return render(request, 'myadmin/users.html', context)


def deleteuser(request, email):
    if not request.session.get('user_permission') == 'admin':
        return redirect(myadmin)

    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"delete from user where email='{email}'"
    cr.execute(q)
    con.commit()
    con.close()

    return redirect(users)


def orders(request):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)

    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    if request.POST:
        id = request.POST.get('id')
        paystatus = request.POST.get('paystatus')
        q = f"update billing set paystatus='{paystatus}' where bill_id={id}"
        cr.execute(q)
        con.commit()

    q = f"select * from billing order by bill_id desc"
    cr.execute(q)
    data = []
    for i in cr.fetchall():
        data.append({'id': i[0], 'name': i[1], 'email': i[2], 'address': i[3], 'amount': i[4], 'mobile': i[5],
                     'typeofbill': i[6], 'dateofpayment': i[7], 'paystatus': i[8]})
    context['data'] = data
    con.close()
    return render(request, 'myadmin/orders.html', context)


def orderdetail(request, bid):
    if not request.session.get('user_permission') in adminlogin:
        return redirect(myadmin)

    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select * from billDetail where  billing_id = {bid}"
    cr.execute(q)
    data = []
    for i in cr.fetchall():
        data.append({'id': i[0], 'title': i[1], 'price': i[2], 'qty': i[3], 'total': i[4]})
    context['data'] = data
    context['total'] = sum(i['total'] for i in data)
    return render(request, 'myadmin/orderdetail.html', context)


# client views

def home(request):
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select id,name,priceAfterdiscount,photo from product"
    cr.execute(q)
    data = []
    res = cr.fetchall()
    for j in range(5):
        i = random.choice(res)
        res.remove(i)
        data.append({'id': i[0], 'name': i[1], 'price': i[2], 'photo': i[3]})

    context['data'] = data

    con.close()
    return render(request, 'client/index.html', context)


def single(request, id):
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select * from product where id={id}"
    cr.execute(q)
    data = cr.fetchone()

    q = f"select name from category where id={data[6]}"
    cr.execute(q)
    category_name = cr.fetchone()
    context['data'] = {'id': data[0], 'name': data[1], 'price': data[2], 'priceAfterdiscount': data[3],
                       'description': data[4], 'brand': data[5], 'photo': data[7], 'category': category_name}

    q = f"select id,name,priceAfterdiscount,photo from product where id!={id} and category_id={data[6]}"
    cr.execute(q)
    res = cr.fetchall()

    related_data = []
    for j in range(3):
        i = random.choice(res)
        res.remove(i)
        related_data.append({'id': i[0], 'name': i[1], 'price': i[2], 'photo': i[3]})

    context['related_data'] = related_data
    con.close()

    return render(request, 'client/single.html', context)


def account(request):
    if request.session.get('user'):
        return redirect(home)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = hash_password(email, request.POST.get('password'))

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = f"select * from user"
        cr.execute(q)

        for i in cr.fetchall():
            if i[1] == email and i[2] == password:
                request.session['user'] = i[0]
                request.session['user_permission'] = i[3]
                con.close()
                return redirect(home)

    return render(request, 'client/account.html')


def register(request):
    if request.session.get('user'):
        return redirect(home)

    if request.method == "POST":
        otp = request.POST.get('otp')
        regData = request.session.get('regData')

        if otp != regData['otp']:
            return HttpResponse("OTP Doesn't match")

        name = regData.get('name').lower()
        email = regData.get('email').lower()
        password = hash_password(email, regData.get('password'))

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = "select email from user"
        cr.execute(q)
        for i in cr.fetchall():
            if i[0] == email:
                return HttpResponse('Email Already Registered',status=404)

        q = f"""insert into user values("{name}","{email}","{password}","user")"""
        cr.execute(q)
        con.commit()
        del request.session['regData']
        con.close()
        return redirect(account)

    return render(request, 'client/register.html')



def sentOtp(request):
    name = request.POST['name']
    email = request.POST['email']
    password = request.POST['password']
    otp = mail.send_Mail(email)
    request.session['regData'] = {'name': name, 'email': email, 'password': password, 'otp': otp}
    return HttpResponse('sent')


def categorynames(request):
    if request.method == 'GET':

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = f"select id, name from category order by name"
        cr.execute(q)
        data = []
        for i in cr.fetchall():
            data.append({'id': i[0], 'category': i[1]})

        return JsonResponse({'data': data})


def products(request, id):
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    if id:
        q = f"select id,name,priceAfterdiscount,description,photo from product where category_id = {id}"
    else:
        q = f"select id,name,priceAfterdiscount,description,photo from product"

    cr.execute(q)
    data = []
    for i in cr.fetchall():
        data.append({'id': i[0], 'name': i[1], 'price': i[2], 'description': i[3], 'photo': i[4]})

    paginator = Paginator(data, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['data'] = page_obj
    context['pages'] = range(1, int(page_obj.paginator.num_pages + 1)) if page_obj.paginator.num_pages > 1 else None
    return render(request, 'client/products.html', context)


def empty_cart(request):
    if request.session.get('cart'):
        del request.session['cart']

    return HttpResponse(status=200)


def add_to_cart(request, id):
    if not request.session.get('cart'):
        request.session['cart'] = []

    all_items = request.session['cart']
    for i in all_items:
        if i['id'] == id:
            i['qty'] += 1
            i['total'] += i['price']
            request.session['cart'] = all_items
            total = sum(i['total'] for i in request.session.get('cart'))

            return JsonResponse({'total': total, 'length': len(request.session.get('cart'))})

    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select id,name,priceAfterdiscount,photo from product where id={id}"
    cr.execute(q)
    res = cr.fetchone()
    con.close()
    all_items.append(
        {
            'id': res[0],
            'name': res[1],
            'price': float(res[2]),
            'photo': res[3],
            'qty': 1,
            'total': float(res[2])
        }
    )
    request.session['cart'] = all_items
    total = sum(i['total'] for i in request.session.get('cart'))

    return JsonResponse({'total': total, 'length': len(request.session.get('cart'))})


def checkout(request):
    if not request.session.get('cart'):
        return render(request, 'client/checkout.html')

    total = sum(i['total'] for i in request.session.get('cart'))
    return render(request, 'client/checkout.html', {'data': request.session.get('cart'), 'total': total})


def inc_dec(request, id, operation):
    all_items = request.session.get('cart')
    for i in all_items:
        if i['id'] == id:
            if operation == 'plus':
                i['qty'] += 1
                i['total'] += i['price']
                break
            elif operation == 'minus':
                if i['qty'] == 1:
                    all_items.remove(i)
                    break
                else:
                    i['qty'] -= 1
                    i['total'] -= 1
                    break
            elif operation == 'remove':
                all_items.remove(i)
                break
    request.session['cart'] = all_items
    return HttpResponse(status=200)


def contact(request):
    return render(request, 'client/contact.html')


def proceed_to_pay(request):
    if not request.session.get('cart') or not request.session.get('user'):
        return HttpResponse('Not Found', status=404)

    total = sum(i['total'] for i in request.session.get('cart'))
    return render(request, 'client/proceed_to_pay.html', {'total': total})


def payment_action(request):
    name = request.POST['name']
    email = request.POST['email']
    address = request.POST['address']
    total = request.POST['total']
    paymentmode = request.POST['paymentmode']
    from datetime import date
    mobile = request.POST['mobile']
    dateOfOrder = date.today()

    if paymentmode == 'Cash':
        payStatus = 'pending'
    else:
        payStatus = 'paid'
    # print(request.session.get('cart'))

    conn = sqlite3.connect('db.sqlite3')
    cr = conn.cursor()
    Query_for_bill = f"""insert into billing (`email`, `address`, `totalAmount`, `mobile`, `typeofbill`, `dateofpayment`, `paystatus`,`name`) values ("{email}", "{address}","{total}", "{mobile}","{paymentmode}","{dateOfOrder}", "{payStatus}","{name}")"""
    cr.execute(Query_for_bill)
    conn.commit()

    select_query = "select bill_id from billing order by bill_id DESC"
    cr = conn.cursor()
    cr.execute(select_query)
    result = cr.fetchone()

    for item in request.session['cart']:
        query_detail = f"""insert into billDetail (`title`, `price`, `qty`, `total_price`, `billing_id`) values ("{item['name']}","{item['price']}","{item['qty']}","{item['total']}","{result[0]}")"""
        cr = conn.cursor()
        cr.execute(query_detail)
        conn.commit()

    body = f"""
        <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            </head>
            <body>
            Thank You for shopping with E-Shop {name}. Your Order will be delivered soon at {address}.
            Your will be informed for delivery at your Mobile Number: {mobile}.\n
            Your Billing ID is {result[0]}. 
            For more information Please Contact at 8054052772(Customer Care).\n\n 
            <table style="border=1;">
            <thead>
            <th>Name</th>
            <th>Quantity</th>
            <th>Total</th>
            </thead>
            <tbody>
        """
    for i in request.session.get('cart'):
        body += f"""
            <tr>
            <td>{i['name']}</td>
            <td style="text-align:center;">{i['qty']}</td>
            <td>{i['total']}</td>
            </tr>
            """
    body += f"""
        <th colspan=2>Grand Total</th>
        <th>{total}</th>
        """
    body += """
        </tbody>
        </table>
        </body>
        """
    mail.send_Receipt(email, body)
    return JsonResponse({'billid': result[0]})


def thankspage(request):
    try:
        del request.session['cart']
    except:
        pass
    billid = request.GET['billid']
    return render(request, 'client/thankyou.html', {'billid': billid})


# end of client views


def TnC(request):
    return render(request, 'client/TnC.html')


def privacy(request):
    return render(request, 'client/privacy.html')
