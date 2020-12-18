from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
import sqlite3
from django.contrib import messages
from hashlib import sha3_512
import random
from django.views.decorators.csrf import csrf_exempt

adminlogin = ('staff', 'admin')


def myadmin(request):
    if request.session.get('user_permission') in adminlogin:
        return redirect(adminhome)

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = sha3_512(request.POST.get('password').encode('utf-8')).hexdigest()
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
    request.session.clear()
    return redirect(myadmin)


def userlogout(request):
    request.session.clear()
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

        q = f"insert into category values(NULL,'{name}','{description}')"
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
    q = f"select id,name,description from category"
    cr.execute(q)
    data = []

    for row in cr.fetchall():
        data.append({'id': row[0], 'name': row[1], 'description': row[2]})
    data.sort(key=lambda x: x.get('name'))

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

        q = f"update category set name='{name}', description='{description}' where id={id}"
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
        q = f"insert into product values (NULL ,'{name}',{price},{priceafterdiscount},'{description}','{brand}',{category},'{fileurl}')"
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

    q = "select * from product"
    cr.execute(q)
    data = []
    for i in cr.fetchall():
        data.append({'id': i[0], 'name': i[1], 'price': i[2], 'priceafter': i[3], 'description': i[4],
                     'brand': i[5], 'category': category[i[6]], 'photo': i[7]})
    data.sort(key=lambda x: x.get('name'))

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
            q = f"update product set name='{name}', price={price}, priceAfterdiscount=" \
                f" {priceafterdiscount},description='{description}',brand='{brand}'," \
                f"category_id={category},photo = '{fileurl}' where id={id}"
            cr.execute(q)
            con.commit()
            messages.add_message(request, messages.SUCCESS,
                                 'Product Updated Successfully')
            con.close()

            return redirect(viewproduct)

        else:
            q = f"update product set name='{name}', price={price}, priceAfterdiscount=" \
                f" {priceafterdiscount},description='{description}',brand='{brand}'," \
                f"category_id={category} where id={id}"
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

    q = f"select name,email,permission from user"
    cr.execute(q)
    data = []

    for i in cr.fetchall():
        data.append({'name': i[0], 'email': i[1], 'permission': i[2]})
    data.sort(key=lambda x: x.get('name'))

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


# client views

def home(request):
    context = {}
    con = sqlite3.connect('db.sqlite3')
    cr = con.cursor()
    q = f"select id,name,priceAfterdiscount,photo from product"
    cr.execute(q)
    data = []
    res = random.choices(cr.fetchall(), k=5)

    for i in res:
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
    res = random.choices(cr.fetchall(), k=3)
    related_data = []
    for i in res:
        related_data.append({'id': i[0], 'name': i[1], 'price': i[2], 'photo': i[3]})
    context['related_data'] = related_data
    con.close()

    return render(request, 'client/single.html', context)


def account(request):
    if request.session.get('user'):
        return redirect(home)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = sha3_512(request.POST.get('password').encode('utf-8')).hexdigest()

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
        name = request.POST.get('name').lower()
        email = request.POST.get('email').lower()
        password = sha3_512(request.POST.get('password1').encode('utf-8')).hexdigest()

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = "select email from user"
        cr.execute(q)
        for i in cr.fetchall():
            if i[0] == email:
                return redirect(register)

        q = f"insert into user values('{name}','{email}','{password}','user')"
        cr.execute(q)
        con.commit()
        con.close()
        return redirect(account)

    return render(request, 'client/register.html')


def categorynames(request):
    if request.method == 'GET':

        con = sqlite3.connect('db.sqlite3')
        cr = con.cursor()
        q = f"select id, name from category"
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

    context['data'] = data
    return render(request, 'client/products.html', context)


def empty_cart(request):
    if request.session.get('cart'):
        del request.session['cart']

    return HttpResponse(status=200)


def add_to_cart(request, id):
    if not request.session.get('cart'):
        request.session['cart'] = []
    total = 0
    # if any([i['id'] == id for i in request.session.get('cart')]):
    #     return JsonResponse({},status=406)
    #
    # con = sqlite3.connect('db.sqlite3')
    # cr  = con.cursor()
    # q = f"select id,name, priceAfterdiscount,photo from product where id = {id}"
    # cr.execute(q)
    # i = cr.fetchone()
    #
    return JsonResponse({'total':total})


def checkout(request):
    return render(request, 'client/checkout.html')


def contact(request):
    return render(request, 'client/contact.html')


# end of client views


def TnC(request):
    return render(request, 'client/TnC.html')


def privacy(request):
    return render(request, 'client/privacy.html')
