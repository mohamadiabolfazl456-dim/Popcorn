
import sys
import os
import math
import re
import time
import urllib.request
import urllib.error
import urllib.parse
import ssl
import json
import http.cookiejar
import pprint
'''
قابلیت های جدید
💎شماره خط خطا رو نشون میده
💎قابلیت range پایتون برای لیست عدد
list nums=i[0..10]  [0,1,2....10]
list nums=i[0..<10]  [0,1,2....9]  روند افزایشی
و برعکس
list nums=i[10..0]  [10,9,8....0]  روند کاهشی
list nums=i[10..<0]  [10,9,8....1]
پشتیبانی از لیست و آرایه.
list names=s[^jim^,^tom^]       برای رشته
list ages=i[18,19]         برای عدد های صحیح
درسترسی خوب در ۹۰٪دستورات فعلی و حتی ذخیره داده با محاسبه
و همینطور
arr names=s{^ali^}
arr ages=i{18}
arr name_age=m{^ali^,18,^abolfazl_mohamadi^,18}    این برای ذخیره ترکیبی
نگه داری تفکیک شده داده ها در دیکشنری های متفاوت.
'''

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

# این دو خط مهم رو دقیقاً اینجا اضافه کن
urllib.request.custom_headers = {}          # دیکشنری هدرهای سفارشی (همیشه وجود داشته باشه)
urllib.request.cookie_jar = None            # برای کوکی‌ها (بعداً فعال می‌شه)

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
version="""1.5_Pro"""
current_line_number = 0   # شماره خط فعلی

variables = {}
constable = {}
#functions
# دیکشنری‌های مربوط به توابع
#functions = {}      # {'name': {'params': ['x', 'y'], 'code': ['line1', 'line2', ...]}}
#func_locals = {}    # موقع اجرا: متغیرهای محلی هر تابع
#arrays
array={}
#
listStr={}
listInt={}
#null
files={}

# برای جلوگیری از خطای SSL در برخی محیط‌ها (اختیاری)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_page(url):
    try:
        # ساخت درخواست
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) AppleWebKit/537.36 Safari/537.36'
                # بسیاری از سایت‌ها درخواست‌های بدون User-Agent را بلاک می‌کنند
            }
        )
        
        # ارسال درخواست و دریافت پاسخ
        with urllib.request.urlopen(req, context=ctx) as response:
            # خواندن محتوا به صورت بایت
            html_bytes = response.read()
            
            # تشخیص خودکار انکودینگ و تبدیل به رشته
            encoding = response.headers.get_content_charset() or 'utf-8'
            html = html_bytes.decode(encoding)
            
            print(f"وضعیت پاسخ: {response.status} {response.reason}")
            print(f"طول محتوا: {len(html)} کاراکتر")
            return html
            
    except urllib.error.HTTPError as e:
        print(f"خطای HTTP: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print(f"خطای اتصال: {e.reason}")
    except Exception as e:
        print(f"خطای غیرمنتظره: {e}")
p_dim_cache = {}
#پارسر عبارت منطقی
def cond(expr, variables=None, array=None, constable=None):
    """
    پارس کردن شرط به سبک C++/Java
    پشتیبانی کامل از: && || ! == != > < >= <= ( )
    """
    if variables is None: variables = globals().get('variables', {})
    if array is None: array = globals().get('array', {})
    if constable is None: constable = globals().get('constable', {})

    expr = expr.strip()
    if not expr:
        return False

    # جایگزینی متغیرها و آرایه‌ها با مقدارشون
    def replace_var(match):
        name = match.group(0)
        if name in variables:
            val = variables[name]
            return 'True' if val else 'False'
        if name in constable:
            val = constable[name]
            return 'True' if val else 'False'
        
        # پشتیبانی از آرایه: arr[0] یا arr[^ali^]
        arr_match = re.match(r'([a-zA-Z_]\w*)\[(.+?)\]', name)
        if arr_match:
            arr_name, idx = arr_match.groups()
            if arr_name not in array:
                return 'False'
            arr_val = array[arr_name]
            if idx.startswith('^') and idx.endswith('^'):
                search = idx[1:-1]
                try:
                    return 'True' if search in [str(x) for x in arr_val] else 'False'
                except:
                    return 'False'
            else:
                try:
                    i = int(idx)
                    return 'True' if -len(arr_val) <= i < len(arr_val) else 'False'
                except:
                    return 'False'
        return 'False'

    # جایگزینی همه متغیرها
    expr = re.sub(r'\b[a-zA-Z_]\w*(?:\[[^\]]+\])?\b', replace_var, expr)

    # تبدیل عملگرهای C++ به پایتون
    expr = expr.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')

    # حالا eval امن
    try:
        return eval(expr, {"__builtins__": {}}, {'True': True, 'False': False})
    except Exception as e:
        err(f"خطا در شرط: {expr} → {e}")
        return False
#پارسر عبارات
def p_dim(expr, variables, array=None, constable=None):
    """
    محاسبه امن عبارت ریاضی و منطقی با پشتیبانی از:
    پرانتز، اولویت عملگرها، متغیرها، دسترسی به آرایه، مقایسهها
    مثالها:
        p_dim("2 + 3 * (4 - 1)", vars) → 11
        p_dim("x >= 5 && y < 10", vars) → True یا False
        p_dim("arr1[2] + 5", vars, array) → مقدار عددی
    """
    if array is None:
        array = {}
    if constable is None:
        constable = {}

    expr = expr.strip()
    if not expr:
        return 0

    # کش کردن (اختیاری — سرعت رو خیلی بالا می‌بره)
    cache_key = (expr, id(variables), id(array), id(constable))
    if cache_key in p_dim_cache:
        return p_dim_cache[cache_key]

    # توکنایزر ساده اما بسیار قدرتمند
    token_pattern = r'''
        (\()\s*       |     # پرانتز باز
        \s*\)         |     # پرانتز بسته
        \s*([+\-*/^]) \s* | # عملگرهای ریاضی
        \s*(>=|<=|==|!=|>|<) \s* |  # عملگرهای مقایسه
        \s*(&&|\|\|) \s*   |        # AND و OR منطقی
        \s*(\d+\.?\d*) \s* |        # عدد (اعشاری یا صحیح)
        \s*([a-zA-Z_]\w*(?:\[[^\]]+\])?) \s*  # متغیر یا arr[2] یا arr[^ali]
    '''
    tokens = [t.strip() for t in re.split(token_pattern, expr) if t.strip() or t in '()']
    tokens = [t for t in '()+-*/^>=<==!=&&||' or t for t in tokens if t]

    def parse(tokens, pos=0):
        values = []
        operators = []

        def apply_op():
            if len(values) < 2 or not operators:
                raise ValueError("عملگر بدون عملوند")
            b = values.pop()
            a = values.pop()
            op = operators.pop()

            if op == '+': values.append(a + b)
            elif op == '-': values.append(a - b)
            elif op == '*': values.append(a * b)
            elif op == '/':
                if b == 0:
                    raise ZeroDivisionError("تقسیم بر صفر")
                values.append(a / b)
            elif op == '^': values.append(a ** b)
            elif op in ('==', '!=', '>', '<', '>=', '<='):
                cmp_map = {'==': a == b, '!=': a != b, '>': a > b, '<': a < b, '>=': a >= b, '<=': a <= b}
                result = cmp_map[op]
                values.append(result)
            elif op == '&&': values.append(a and b)
            elif op == '||': values.append(a or b)

        while pos < len(tokens):
            tok = tokens[pos]

            if tok == '(':
                pos, val = parse(tokens, pos + 1)
                values.append(val)
            elif tok == ')':
                while operators:
                    apply_op()
                if not values:
                    raise ValueError("پرانتز نامتعادل")
                result = values.pop()
                p_dim_cache[cache_key] = result
                return pos, result

            elif tok in '+-*/^>=<==!=&&||':
                while (operators and
                       operators[-1] in '*^' or
                       (operators[-1] in '*/' and tok in '+-') or
                       (operators[-1] in '+-' and tok in '+-') or
                       (operators[-1] in ('==','!=','>','<','>=','<=') and tok in ('==','!=','>','<','>=','<=','&&','||'))):
                    apply_op()
                operators.append(tok)

            else:
                # عدد یا متغیر یا arr[expr]
                if re.match(r'^-?\d+\.?\d*$', tok):
                    values.append(float(tok) if '.' in tok else int(tok))
                else:
                    # متغیر ساده
                    if tok in variables:
                        values.append(variables[tok])
                    elif tok in constable:
                        values.append(constable[tok])
                    elif '[' in tok and ']' in tok and array:
                        # دسترسی به آرایه: myarr[5] یا myarr[^ali]
                        try:
                            arr_name, idx_part = tok.split('[', 1)
                            idx_part = idx_part[:-1].strip()
                            arr = array[arr_name]
                            if idx_part.startswith('^'):
                                val = idx_part[1:].strip().strip('"').strip("'")
                                str_arr = [str(x) for x in arr]
                                if val in str_arr:
                                    values.append(arr[str_arr.index(val)])
                                else:
                                    raise KeyError(f"مقدار ^'{val}' در آرایه پیدا نشد")
                            else:
                                idx = int(idx_part)
                                values.append(arr[idx])
                        except Exception as e:
                            raise NameError(f"خطا در دسترسی به آرایه {tok}: {e}")
                    else:
                        raise NameError(f"متغیر یا آرایه تعریف‌نشده: {tok}")

            pos += 1

        while operators:
            apply_op()

        if len(values) != 1:
            raise ValueError("عبارت نامعتبر")
        result = values[0]
        p_dim_cache[cache_key] = result
        return pos, result

    try:
        _, result = parse(tokens)
        return result
    except Exception as e:
        err(f"خطا در محاسبه عبارت «{expr}»: {e}")
        return 0
####################################

#

#
def EXIT(code):
	#EXIT(0)
	inside=code[5:-1]
	if inside in ['0','off','end','exit']:
		try:
			sys.exit(0)
		except SystemExit:
			raise
		except Exception as e:
			err('دستور EXIT()اشتباه نوشته شده و یا مقدار داخل پرانتز معتبر نیست')
	else:
		err('مقدار داخل پرانتز نامعتبر از 0,off,end,exit استفاده کن')
#تابع put()
def put(code):
	inside = code[4:-1]
	parts = inside.split(',')
#پیمایش دستور
	for i, part in enumerate(parts):
		part = part.strip()
		if part.startswith('^') and part.endswith('^'):
				#تبدیل کاراکتر های خاص
			mess_print = part[1:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
			print(mess_print, end='')
		#برش رشته داخلی
		# داخل تابع put() — جایگزین بخش قبلی که part رو پردازش می‌کرد
		# تبدیل به حروف بزرگ - uper(^text^) یا uper(name)
		# محاسبه طول — len(^text^) یا len(name) یا len(arr) یا حتی len(text=>[0:5])
# جایگزینی رشته — replace(^old^,^new^,source)

		elif part.startswith('len(') and part.endswith(')'):
			try:
				inner = part[4:-1].strip()  # محتوای داخل پرانتز

				# حالت ۱: len(^متن مستقیم^)
				if (inner.startswith('^') and inner.endswith('^')) or (inner.startswith('#') and inner.endswith('#')):
					text = inner[1:-1].replace('_', ' ').replace('\\n','\n').replace('\\t','\t').replace('\\s',' ')
					print(len(text), end='')

				# حالت ۲: len(name=>[0:5]) — برش رشته
				elif '=>' in inner and inner.endswith(']'):
					# اول برش رو انجام بده، بعد طولش رو بگیر
					try:
						left, slice_part = inner.split('=>', 1)
						var_name = left.strip()
						if var_name not in variables:
							print("[VarNotFound]", end='')
							continue
						source = variables[var_name]
						if not isinstance(source, str):
							print("[NotStr]", end='')
							continue
						if not slice_part.startswith('[') or not slice_part.endswith(']'):
							print(0, end='')
							continue
						slice_str = slice_part[1:-1].strip()
						if ':' not in slice_str:
							print(0, end='')
							continue
						start_str, end_str = slice_str.split(':', 1)
						start = None if not start_str.strip() else int(eval(start_str.strip(), {}, {**variables, **constable, **array,**listStr,**listInt}))
						end = None if not end_str.strip() else int(eval(end_str.strip(), {}, {**variables, **constable, **array,**listStr,**listInt}))
						sliced = source[start:end]
						print(len(sliced), end='')
					except:
						print("[SliceErr]", end='')

				# حالت ۳: len(name) — نام متغیر
				elif inner in variables:
					val = variables[inner]
					if isinstance(val, str):
						print(len(val), end='')
					elif isinstance(val, list):  # آرایه
						print(len(val), end='')
					else:
						print(len(str(val)), end='')  # برای عدد، بول و ...

				# حالت ۴: len(constant)
				elif inner in constable:
					val = constable[inner]
					print(len(str(val)), end='')

				else:
					print(0, end='')  # اگه هیچی نبود

			except Exception as e:
				print("[LenErr]", end='')
		elif part.startswith('upper(') and part.endswith(')'):
			try:
				inner = part[6:-1].strip()  # متن داخل پرانتز
				text = ""

				# اگر داخل ^...^ باشه
				if (inner.startswith('^') and inner.endswith('^')) or (inner.startswith('#') and inner.endswith('#')):
					text = inner[1:-1]
					text = text.replace('_', ' ').replace('\\n','\n').replace('\\t','\t').replace('\\s',' ')
				
				# اگر نام متغیر باشه
				elif inner in variables:
					text = str(variables[inner])
				elif inner in constable:
					text = str(constable[inner])
				else:
					text = inner  # خام چاپ بشه اگه اشتباه بود

				print(text.upper(), end='')

			except Exception as e:
				print("[UperErr]", end='')

		# تبدیل به حروف کوچک - lwer(^Text^) یا lwer(name)
		elif part.startswith('lower(') and part.endswith(')'):
			try:
				inner = part[6:-1].strip()
				text = ""

				if (inner.startswith('^') and inner.endswith('^')) or (inner.startswith('#') and inner.endswith('#')):
					text = inner[1:-1]
					text = text.replace('_', ' ').replace('\n', '\n').replace('\\t', '\t').replace('\\s', ' ')
				elif inner in variables:
					text = str(variables[inner])
				elif inner in constable:
					text = str(constable[inner])
				else:
					text = inner

				print(text.lower(), end='')

			except Exception as e:
				print("[LwerErr]", end='')
				
#

#
		elif part.startswith('count(') and part.endswith(')'):
			inner = part[6:-1].strip()                      # محتوای داخل count(...)
			try:
				if '=>' not in inner:
					print("[CountSyntaxError]", end='')
					continue

				var_name, search_part = [p.strip() for p in inner.split('=>', 1)]

				# بررسی وجود متغیر اصلی
				if var_name not in variables:
					print("[VarNotFound]", end='')
					continue

				source = variables[var_name]
				if not isinstance(source, str):
					print("[NotString]", end='')
					continue

				# استخراج متن جستجو – پشتیبانی از همه حالت‌های رایج
				if search_part.startswith('^') and search_part.endswith('^'):
					search_text = search_part[1:-1]
				elif search_part.startswith('#') and search_part.endswith('#'):
					search_text = search_part[1:-1]
				elif search_part.startswith('"') and search_part.endswith('"'):
					search_text = search_part[1:-1]
				elif search_part.startswith("'") and search_part.endswith("'"):
					search_text = search_part[1:-1]
				elif search_part in variables:
					search_text = str(variables[search_part])
				elif search_part in constable:
					search_text = str(constable[search_part])
				else:
					search_text = search_part                     # متن خام

				# جایگزینی کاراکترهای خاص (مانند سایر بخش‌های Dim)
				search_text = search_text.replace('_', ' ') \
				                         .replace('\\n', '\n') \
				                         .replace('\\t', '\t') \
				                         .replace('\\s', ' ')

				# انجام شمارش و چاپ نتیجه
				print(source.count(search_text), end='')

			except Exception as e:
				print(f"[CountError:{type(e).__name__}]", end='')

#
		elif part.startswith('replace(') and part.endswith(')'):
			try:
				inner = part[8:-1].strip()
				if inner.count(',') != 2:
					print("[ReplaceSyntaxErr]", end='')
					continue

				old_part, new_part, source_part = [p.strip() for p in inner.split(',', 2)]

				# استخراج متن قدیمی
				if old_part.startswith('^') and old_part.endswith('^'):
					old_text = old_part[1:-1].replace('_', ' ').replace('\\n','\n').replace('\\t','\t').replace('\\s',' ')
				elif old_part in variables:
					old_text = str(variables[old_part])
				elif old_part in constable:
					old_text = str(constable[old_part])
				else:
					old_text = old_part

				# استخراج متن جدید
				if new_part.startswith('^') and new_part.endswith('^'):
					new_text = new_part[1:-1].replace('_', ' ').replace('\\n','\n').replace('\\t','\t').replace('\\s',' ')
				elif new_part in variables:
					new_text = str(variables[new_part])
				elif new_part in constable:
					new_text = str(constable[new_part])
				else:
					new_text = new_part

				# استخراج منبع (متغیر، ثابت یا برش رشته)
				if '=>' in source_part and source_part.endswith(']'):
					left, slice_part = source_part.split('=>', 1)
					var_name = left.strip()
					if var_name not in variables:
						print("[VarNotFound]", end='')
						continue
					source = variables[var_name]
					if not isinstance(source, str):
						print("[NotStr]", end='')
						continue
					slice_str = slice_part[1:-1].strip()
					if ':' not in slice_str:
						print(source, end='')
						continue
					start_str, end_str = slice_str.split(':', 1)
					start = None if not start_str.strip() else int(eval(start_str.strip(), {}, {**variables, **constable, **array, **listStr, **listInt}))
					end   = None if not end_str.strip()   else int(eval(end_str.strip(),   {}, {**variables, **constable, **array, **listStr, **listInt}))
					source = source[start:end]
				elif source_part.startswith('^') and source_part.endswith('^'):
					source = source_part[1:-1].replace('_', ' ').replace('\\n','\n').replace('\\t','\t').replace('\\s',' ')
				elif source_part in variables:
					source = str(variables[source_part])
				elif source_part in constable:
					source = str(constable[source_part])
				else:
					source = source_part

				# انجام جایگزینی
				if isinstance(source, str):
					result = source.replace(old_text, new_text)
					print(result, end='')
				else:
					print("[ReplaceNotStr]", end='')

			except Exception as e:
				print(f"[ReplaceErr:{type(e).__name__}]", end='')
		#sleep داخلی put
		elif part.startswith('slep(') and part.endswith(')'):
			try:
				inside=part[5:-1]
				t=eval(inside, {}, {**variables, **constable, **array,**listStr,**listInt})
				t=int(t)
				time.sleep(t)
			except Exception as e:
				print('',e)
		elif '=>' in part and part.endswith(']'):
			# پشتیبانی از برش مستقیم رشته داخل put
			# مثال: text=>[0:5] یا msg=>[a:b] یا name=>[:10]
			try:
				left, slice_part = part.split('=>', 1)
				var_name = left.strip()

				if var_name not in variables:
					print("[VarNotFound]", end='')
					continue

				source = variables[var_name]
				if not isinstance(source, str):
					print("[NotString]", end='')
					continue

				if not slice_part.startswith('[') or not slice_part.endswith(']'):
					print(part, end='')  # اگه فرمت اشتباه بود، خام چاپ کن
					continue

				slice_str = slice_part[1:-1].strip()  # مثلاً "0:5" یا ":10" یا "a:"

				if ':' not in slice_str:
					print(part, end='')
					continue

				start_str, end_str = slice_str.split(':', 1)
				start = None if not start_str.strip() else int(eval(start_str.strip(), {}, {**variables, **constable, **array,**listStr,**listInt}))
				end = None if not end_str.strip() else int(eval(end_str.strip(), {}, {**variables, **constable, **array,**listStr,**listInt}))

				result = source[start:end]
				print(result, end='')

			except Exception as e:
				print("[SliceErr]", end='')
			#فرمت در چاپ
		elif (part.startswith('f^') and part.endswith('^')) or (part.startswith('F^') and part.endswith('^')):
		
			mess_print = part[2:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
			try:
		# با استفاده از format_map متغیرها و ثابت‌ها را در {} جای‌گذاری می‌کنه
				formatted = mess_print.format_map({**variables, **constable,**array,**listStr,**listInt})
				print(formatted, end='')
	
			except KeyError as e:
				print(f"[Missing:{e}]", end='')
			#محاسبه عبارت پایتونی
		elif part.startswith('~') and part.endswith('~'):
			eval_print = part[1:-1]
			try:
				result = eval(eval_print, {}, {**variables, **constable,**array,**listStr,**listInt})
		# اگر نتیجه رشته‌ای باشه و عددی داخلش باشه، تبدیلش کن
				print(result, end='')
			except Exception as e:
				print(f"[EvalErr:{e}]", end='')
			#اگر نام متغییر یا ثابت آمد
		elif part in variables:
			print(variables[part], end='')
		elif part in constable:
			print(constable[part], end='')
		else:
			print('', end='')
		if i < len(parts)-1:
			print('', end='')
	print()

#تابع inp()
def inp(code):
	value=None
	try:
		inside = code[4:-1]			
		name, mess = inside.split(',', 1)
	except:
		err('inp syntax must be inp(name,^message^)')
		return
	name = name.replace(' ','')
		#اگر نام از داخل ثابت ها بود
	if name in constable:
		err(f"نمی‌توان مقدار ورودی را به ثابت '{name}' داد")
		return
		#حالت معمول تعریف متغییر در ورودی
	if (mess.startswith('^') and mess.endswith('^')) or (mess.startswith('#') and mess.endswith('#')):
		mess = mess[1:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
		value = input(mess)
		variables[name] = value
		#گرفتن ورودی از جنس عدد
	elif (mess.startswith('i^') and mess.endswith('^')) or (mess.startswith('i#') and mess.endswith('#')):
		mess = mess[2:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
		try:
			formatted = mess.format_map({**variables, **constable,**array,**listStr,**listInt})
		# گرفتن ورودی با پیام فرمت‌شده
				
			value=int(input(formatted))
		except ValueError as e:
			err('ورودی عدد نیست')
			value=0
		variables[name]=value
		#گرفتن ورودی از جنس اعشار
	elif (mess.startswith('d^') and mess.endswith('^')) or (mess.startswith('d#') and mess.endswith('#')):
		mess = mess[2:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
		try:
			formatted = mess.format_map({**variables, **constable,**array,**listStr,**listInt})
			value=float(input(formatted))
		except ValueError as e:
			err('ورودی اعشار نیست')
			value=0.0
		variables[name]=value
		#گرفتن ورودی بول
	elif (mess.startswith('b^') and mess.endswith('^')) or (mess.startswith('b#') and mess.endswith('#')):
		mess = mess[2:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n','\n')
		try:
			formatted = mess.format_map({**variables, **constable,**array,**listStr,**listInt})
			raw=input(formatted).strip().upper()
			if raw in ['1','YES','OK','ON','TRUE']:
				value=True
				variables[name]=value
			elif raw in ['0','NO','NOT','OFF','FALSE']:
				value=False
				variables[name]=value
			else:
				err('مقدار بول نیست')
				
		except ValueError as e:
			err('ورودی بول نیست')
			
		#ورودی با فرمت
	elif (mess.startswith('f^') and mess.endswith('^')) or (mess.startswith('$^') and mess.endswith('^')):
		mess = mess[2:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t', '	').replace('\\n',"""\n""")
		try:
		# جایگذاری متغیرها و ثابت‌ها در پیام
			formatted = mess.format_map({**variables, **constable,**array,**listStr,**listInt})
		# گرفتن ورودی با پیام فرمت‌شده
			value = input(formatted)
			variables[name] = value
		except KeyError as e:
			print(f"[Missing:{e}]")
		#اگر قرار باشه ورودی بدون متغییر باشه
	elif name.lower() in ['null','¿']:
		if (mess.startswith('^') and mess.endswith('^')) or (mess.startswith('#') and mess.endswith('#')):
				#تبدیل کاراکتر های خاص
			mess = mess[1:-1].replace('_', ' ').replace('\\s', ' ').replace('\\t','	').replace('\\n',"""\n""")
		input(mess)
	else:
		err('فرمت نادرست برای پیام ورودی')
#تابع error()
def err(msg):
	global current_line_number
	if current_line_number > 0:
		print(f"[Error - خط {current_line_number}] {msg}")
	else:
		print(f"[Error] {msg}")
#تابع قلب
#___________dim heart__________________________
def run_line(cod):
	code = cod.strip()
	# پشتیبانی از چند دستور در یک خط با جداکننده ;
	if ';;;' in code:
		parts = [p.strip() for p in code.split(';;;') if p.strip()]
		for part in parts:
			run_line(part)
		return
	elif not code:
		return

	code = code.replace(' ', '')
	
	# تعریف ثابت con$
	if code.startswith('con$') and '=' in code and not code.startswith('put') and not code.startswith('inp'):
		name, value = code.split('=', 1)
		name = name.replace('con$', '')
		
		if name in constable:
			err("نام ثابت رزرو شده")
			return
		
		if (value.startswith('"') and value.endswith('"')) or \
		   (value.startswith("'") and value.endswith("'")) or \
		   (value.startswith('^') and value.endswith('^')) or \
		   (value.startswith('#') and value.endswith('#')):
			value = value[1:-1]
		else:
			if value in constable:
				value = constable[value]
			else:
				try:
					value = int(value)
				except:
					try:
						value=float(value)
					except:
						try:
							value=str(value)
						except:
							try:
								value=bool(value)
							except:
								err('داده غیر قابل قبول')
					

		constable[name] = value
	#
# ────────────────────────────── تعریف تابع کاربر ──────────────────────────────
# ──────────────────────── تعریف تابع کاربر (fn) ────────────────────────

	#
	elif code.startswith('list') and '=' in code:
		try:
				# حذف کلمه list و جدا کردن نام و مقدار
			rest = code[4:].strip()
			name, value_part = rest.split('=', 1)
			name = name.strip()
			if name in constable:
				err("نمی‌توان لیست را با نام ثابت تعریف کرد")
				return

			value_part = value_part.strip()

				# حالت تعریف لیست رشته‌ای: list names = s["ali", "reza", "sara"]
			if value_part.startswith('s[') and value_part.endswith(']'):
				raw = value_part[2:-1]  # حذف s[ و ]
				items = [item.strip() for item in raw.split(',') if item.strip()]

				clean_items = []
				for item in items:
					item = item.strip()
					if (item.startswith('"') and item.endswith('"')) or \
					   (item.startswith("'") and item.endswith("'")) or \
					   (item.startswith('^') and item.endswith('^')) or \
					   (item.startswith('#') and item.endswith('#')):
						item = item[1:-1]
					clean_items.append(item.replace('_', ' '))

				listStr[name] = clean_items
				

				# حالت لیست خالی
			elif value_part == 's[]':
				listStr[name] = []
			#int list
			elif value_part.startswith('i[') and value_part.endswith(']'):
				content = value_part[2:-1].strip()

				if '..' in content:
					parts = content.split('..')
					if len(parts) != 2:
						err("فرمت range اشتباه است (start..end یا start..<end)")
						return

					start_str, end_str = [p.strip() for p in parts]
					inclusive = not end_str.startswith('<')
					if not inclusive:
						end_str = end_str[1:].strip()

					try:
						start = int(eval(start_str, {}, {**variables, **constable, **array, **listStr, **listInt}))
						end   = int(eval(end_str,   {}, {**variables, **constable, **array, **listStr, **listInt}))
					except:
						err("مقادیر range باید عدد صحیح باشند")
						return

					if start < end:
						nums = list(range(start, end + 1 if inclusive else end))
					elif start > end:
						nums = list(range(start, end - 1 if inclusive else end, -1))
					else:
						nums = [start] if inclusive else []

					listInt[name] = nums
					return

				else:
					items = [item.strip() for item in content.split(',') if item.strip()]
					try:
						listInt[name] = [int(item) for item in items]
					except ValueError:
						err("همه مقادیر در لیست عددی باید عدد صحیح باشند")
					return

				# حالت لیست خالی
			elif value_part == 'i[]':
				listInt[name] = []

			else:
				err('فرمو های معتبر')
				err("s[] و i[]")
				return

		except Exception as e:
			err(f"خطا در تعریف لیست: {e}")

		# ─────────────────────────────────────────────────────────────
		
		#  ─────────────────────────────────────────────────────────────
	elif re.match(r'^[a-zA-Z_]\w*\[\d+\]$', code.strip()):
		try:
			match = re.match(r'^([a-zA-Z_]\w*)\[(\d+)\]$', code.strip())
			if not match:
				err("فرمت دسترسی به لیست اشتباه است")
				return

			list_name = match.group(1)
			index = int(match.group(2))

			if list_name not in listStr:
				err(f"لیست '{list_name}' وجود ندارد")
				return

			the_list = listStr[list_name]

			if index < 1 or index > len(the_list):
				err(f"ایندکس {index} خارج از محدوده است (1 تا {len(the_list)})")
				return

				# تبدیل ایندکس ۱-محور به ۰-محور برای پایتون
			print(the_list[index - 1])

		except Exception as e:
			err(f"خطا در دسترسی به لیست: {e}")
	###
	elif code.startswith("time(") and code.endswith(")"):
		import time as _time_module
		
		inside = code[5:-1].strip()

		if not inside:
			print(int(_time_module.time()))
			return

		parts = [p.strip() for p in inside.split(",")]
		cmd = parts[0].lower() if parts else ""

		# 1. time(now) یا time(date)
		if cmd in ["now", "date", "datetime"]:
			print(f"تاریخ و ساعت فعلی:")
			print(f"  {_time_module.strftime('%Y/%m/%d')}  -  {_time_module.strftime('%H:%M:%S')}")
			print(f"  {_time_module.strftime('%A')}  |  {_time_module.strftime('%d %B %Y')}")

		# 2. time(clock) → ساعت دیجیتال زنده
		elif cmd == "clock":
			print("ساعت دیجیتال - برای خروج Ctrl+C بزنید")
			try:
				while True:
					print("\033[H\033[J", end="")
					current_time = _time_module.strftime("%H:%M:%S")
					current_date = _time_module.strftime("%Y/%m/%d - %A")
					print("╔════════════════════════╗")
					print(f"║        {current_time}        ║")
					print(f"║     {current_date}     ║")
					print("╚════════════════════════╝")
					_time_module.sleep(1)
			except KeyboardInterrupt:
				print("\033[H\033[J", end="")
				print("ساعت متوقف شد.")

		# 3. time(countdown,ثانیه)
		elif cmd == "countdown" and len(parts) >= 2:
			try:
				seconds = int(eval(parts[1], {}, {**variables, **constable, **array,**listStr,**listInt}))
				if seconds <= 0:
					print("[Error] ثانیه باید مثبت باشد")
					return
				print(f"شمارش معکوس {seconds} ثانیه‌ای شروع شد!")
				for i in range(seconds, 0, -1):
					print("\033[H\033[J", end="")
					print(f"\n\n\n\t\t{i}\n\n\t\tثانیه باقی‌مانده")
					if i <= 5:
						print("\a", end="")
					_time_module.sleep(1)
				print("\033[H\033[J", end="")
				print("\n\n\n\t\tزمان تمام شد!")
				print("\a\a\a")
			except Exception as e:
				print(f"[Error] خطا در countdown: {e}")

		# 4. time(timer)
		elif cmd == "timer":
			if "TIMER_START" in variables:
				elapsed = _time_module.time() - variables["TIMER_START"]
				print(f"زمان سپری شده: {elapsed:.3f} ثانیه")
				del variables["TIMER_START"]
			else:
				variables["TIMER_START"] = _time_module.time()
				print("تایمر شروع شد. دوباره time(timer) بزنید تا زمان را ببینید.")

		# 5. time(stamp)
		elif cmd in ["stamp", "unix", "epoch"]:
			print(int(_time_module.time()))

		# 6. time(delay,ثانیه)
		elif cmd == "delay" and len(parts) >= 2:
			try:
				sec = float(eval(parts[1], {}, {**variables, **constable, **array,**listStr,**listInt}))
				_time_module.sleep(sec)
			except:
				print("[Error] مقدار تاخیر باید عدد باشد")

		# 7. time(format,فرمت)
		elif cmd == "format" and len(parts) >= 2:
			fmt = parts[1]
			if fmt.startswith('^') and fmt.endswith('^'):
				fmt = fmt[1:-1]
			elif fmt.startswith('"') and fmt.endswith('"'):
				fmt = fmt[1:-1]
			elif fmt.startswith("'") and fmt.endswith("'"):
				fmt = fmt[1:-1]
			print(_time_module.strftime(fmt))

		else:
			print("[Error] دستور time ناشناخته. دستورات معتبر:")
			print("  time()")
			print("  time(now)")
			print("  time(clock)")
			print("  time(countdown,10)")
			print("  time(timer)")
			print("  time(delay,2)")
			print("  time(format,^%Y/%m/%d %H:%M:%S^)")
	###
	
			
	elif code.startswith('slep(') and code.endswith(')'):
		import time
		inside=code[5:-1]
		r=eval(inside, {}, {**variables, **constable,**array,**listStr,**listInt})
		r=int(r)
		time.sleep(r)
	#string
	elif code.startswith('str') and '=' in code:
		# مثال‌ها:
		# str name = ^سلام دنیا^
		# str sub = text=>[0:5]
		# str mid = msg=>[a:b]
		# str hello = ^سلام ^ + name

		try:
			raw = code[3:]  # حذف "str" از اول
			name, value_part = raw.split('=', 1)
			name = name.strip()

			if not name:
				err("نام متغیر رشته خالی است")
				return

			if name in constable:
				err(f"'{name}' یک ثابت است و نمی‌توان مقدار جدیدی داد")
				return

			value_part = value_part.strip()

			# حالت ۱: رشته خام با ^...^
			if (value_part.startswith('^') and value_part.endswith('^')) or \
			   (value_part.startswith('#') and value_part.endswith('#')):
				value = value_part[1:-1]
				value = value.replace('_', ' ').replace('\\n', '\n').replace('\\t', '\t').replace('\\s', ' ')
				variables[name] = value
			
			###
# حالت ۳: تقسیم رشته → text=>split(^ ^, 3) یا msg=>split(^^)
			elif value_part.startswith("GetCwd()"):
				# حالت بدون پرانتز یا با پرانتز خالی
				try:
					import os
					cwd = os.getcwd()
					variables[name] = cwd
					  # اختیاری، برای دیباگ
				except Exception as e:
					err(f"خطا در گرفتن مسیر فعلی: {e}")
					variables[name] = ""

			elif value_part.startswith("GetCwd(") and value_part.endswith(")"):
				# اگه داخل پرانتز چیزی بود (برای آینده مثلاً GetCwd(format))
				inside = value_part[7:-1].strip()
				if inside:
					err("GetCwd() فعلاً فقط بدون آرگومان کار می‌کنه")
				else:
					try:
						import os
						cwd = os.getcwd()
						variables[name] = cwd
					except Exception as e:
						err(f"خطا در GetCwd(): {e}")
						variables[name] = ""
			elif '=>' in value_part and value_part.endswith(']'):
				if not value_part.count('=>') == 1 or not value_part.count('[') == 1 or not value_part.count(']') == 1:
					err("فرمت برش رشته اشتباه است. مثال: str sub = text=>[0:5]")
					return

				left, right = value_part.split('=>', 1)
				var_name = left.strip()
				slice_part = right.strip()

				if not slice_part.startswith('[') or not slice_part.endswith(']'):
					err("قسمت برش باید با [ و ] احاطه شده باشد")
					return

				slice_str = slice_part[1:-1].strip()  # مثلاً "0:5" یا "a:b" یا ":5" یا "2:"

				if var_name not in variables:
					err(f"متغیر '{var_name}' برای برش تعریف نشده است")
					return
				source = variables[var_name]

				if not isinstance(source, str):
					err(f"متغیر '{var_name}' رشته نیست و نمی‌توان برش زد")
					return

				# تجزیه start:end
				if ':' not in slice_str:
					err("در برش رشته باید از : استفاده شود. مثال: [2:8]")
					return

				start_str, end_str = slice_str.split(':', 1)
				start = None if start_str.strip() == '' else int(eval(start_str.strip(), {}, {**variables, **constable,**array,**listStr,**listInt}))
				end = None if end_str.strip() == '' else int(eval(end_str.strip(), {}, {**variables, **constable,**array,**listStr,**listInt}))

				try:
					result = source[start:end]
					variables[name] = result
				except Exception as e:
					err(f"خطا در برش رشته: {e}")
					variables[name] = ""

			# حالت ۳: الحاق رشته یا استفاده از متغیر
			elif '+' in value_part:
				# پشتیبانی از الحاق ساده: ^سلام^ + name + ^!^
				parts = value_part.replace('+', ' + ').split()
				result = ""
				i = 0
				while i < len(parts):
					p = parts[i]
					if p == '+':
						i += 1
						continue
					if (p.startswith('^') and p.endswith('^')) or (p.startswith('#') and p.endswith('#')):
						result += p[1:-1].replace('_', ' ').replace('\\n', '\n').replace('\\t', '\t')
					elif p in variables:
						result += str(variables[p])
					elif p in constable:
						result += str(constable[p])
					i += 1
				variables[name] = result

			# حالت ۴: کپی از متغیر دیگر
			elif value_part in variables or value_part in constable:
				value = variables.get(value_part) or constable.get(value_part)
				variables[name] = str(value) if value is not None else ""

			# حالت پیش‌فرض: هر چیز دیگه به عنوان رشته ذخیره شود
			else:
				variables[name] = str(value_part)

		except ValueError:
			err("فرمت دستور str اشتباه است. مثال: str name = ^متن^ یا str sub = text=>[0:5]")
		except Exception as e:
			err(f"خطا در دستور str: {e}")
	#داده int
	elif code.startswith('int') and '=' in code:
		name, value = code.split('=', 1)
		name = name.replace('int', '').strip()

		if name in constable:
			err(f"'{name}' یک ثابت است و نمی‌توان مقدار جدیدی داد")
			return

		value = value.strip()

    # حالت ۱: مقدار محاسباتی با ~...~
		if value.startswith('~') and value.endswith('~'):
			expr = value[1:-1].strip()
			try:
				value = eval(expr, {"__builtins__": {}}, {
                **variables, **constable, **array, **listStr, **listInt
            })
			except Exception as e:
				err(f"خطا در محاسبه عبارت: {e}")
				value = 0

    # حالت ۳: مقدار از متغیر یا ثابت دیگر
		elif value in variables:
			value = variables[value]
		elif value in constable:
			value = constable[value]

    # حالت ۴: تبدیل مستقیم به عدد صحیح
		else:
			try:
				value = int(value)
			except ValueError:
				err(f"مقدار '{value}' نمی‌تواند به عدد صحیح تبدیل شود")
				value = 0

    # در نهایت مقدار را ذخیره کنیم
		variables[name] = value if value != "" else None
		#
		#نوع اعشاری
	elif code.startswith('dou') and '=' in code:
		name,value=code.split('=',1)
		name=name.replace('dou','')
		if name in constable:
			err(f"'{name}' یک ثابت است و نمی‌توان مقدار جدیدی داد")
			return
		elif value.startswith('~') and value.endswith('~'):
			value = value[1:-1]
			try:
				value = eval(value, {}, {**variables, **constable,**array,**listStr,**listInt})
		# اگر نتیجه رشته‌ای باشه و عددی داخلش باشه، تبدیلش کن
			except Exception as e:
				print(f"[EvalErr:{e}]", end='')
			#اگر نام متغییر یا ثابت آمد
		else:
			if value in variables:
				value = variables[value]
			elif value in constable:
				value = constable[value]
			else:
				try:
					value = float(value)
				except:
					pass

		variables[name] = value if value != "" else None
		#نوع بول
	elif code.startswith('bol') and '=' in code:
		name, value = code.split('=', 1)
		name = name.replace('bol', '')

		if name in constable:
			err(f"'{name}' یک ثابت است و نمی‌توان مقدار جدیدی داد")
			return

	# حالت محاسبه با ~ ... ~
		elif value.startswith('~') and value.endswith('~'):
			value = value[1:-1]
			try:
				value = eval(value, {}, {**variables, **constable,**array,**listStr,**listInt})
			except Exception as e:
				err(f"EvalErr: {e}")
				value = False  # مقدار پیش‌فرض

	# اگر متغیر یا ثابت است
		elif value in variables:
			value = variables[value]
		elif value in constable:
			value = constable[value]

	# در غیر این صورت رشته یا مقدار مستقیم
		else:
			raw = str(value).strip().upper().replace('^', '').replace("^", '')
			if raw in ['1', 'true', 'yes', 'ok', 'on']:
				value = True
			elif raw in ['0', 'false', 'no', 'off', 'not']:
				value = False
			elif raw in ['¿','null']:
				value=None
			else:
				err(f"مقدار بول معتبر نیست: {value}")
				value = False  # پیش‌فرض ایمن

	# در صورتیکه خروجی eval مقدار عددی یا رشته‌ای باشه، تبدیلش کن
		if isinstance(value, (int, float)):
			value = bool(value)
		elif isinstance(value, str):
			if value.lower() in ['true', 'yes', '1', 'on']:
				value = True
			elif value.lower() in ['false', 'no', '0', 'off']:
				value = False

		variables[name] = value if value != "" else None
	# تعریف متغیر معمولی
	elif code.startswith('var') and '=' in code:
		
		name, value = code.split('=', 1)
		name=name.replace('var','')

		if name in constable:
			err(f"'{name}' یک ثابت است و نمی‌توان مقدار جدیدی داد")
			return

		if (value.startswith('"') and value.endswith('"')) or \
		   (value.startswith("'") and value.endswith("'")) or \
		   (value.startswith('^') and value.endswith('^')) or \
		   (value.startswith('#') and value.endswith('#')):
			value = value[1:-1]
			value=str(value)
			variables[name] = value if value != "" else None
		elif '.' in value:
			value=float(value)
			variables[name] = value if value != "" else None
		elif 'bol' in value:
			value=value.replace('bol','')
			value=bool(value)
			variables[name] = value if value != "" else None
		else:
			if value in variables:
				value = variables[value]
			elif value in constable:
				value = constable[value]
			else:
				try:
					value = int(value)
				except:
					pass

		variables[name] = value if value != "" else None

	# دستور inp(...)
	elif code.startswith("inp") and code[3]=="(" and code[-1]==")":
		inp(code)
		return True
	
	#کامند کردن
	elif code.startswith('*') and code.endswith('*'):
		code=code.replace('*','').replace('*','')
		command=code[1:-1]
		delet=command.replace(command,'')
		
	# دستور put(...)
	elif code.startswith("put") and code[3] == "(" and code[-1] == ")":
		put(code)
	#دستور EXIT()
	elif code.startswith('EXIT') and code[4]=='(' and code[-1]==')':
		code.replace(' ','').lower()
		EXIT(code)
	
	elif code.startswith('fun(') and code.endswith(')'):
		code=code[4:-1].strip()
		var,coden=code.split('=',1)
		if var in variables:
			coden=coden[0:].replace(' ','')
			value = eval(coden, {}, {**variables, **constable,**array,**listStr,**listInt})
			variables[var]=value
		elif 'i:' in var:
			var=var.replace('i:','')
			coden=coden[0:].replace(' ','')
			
			value = eval(coden, {}, {**variables, **constable,**array,**listStr,**listInt})
			value=int(value)
			variables[var]=value
		elif 'd:' in var:
			var=var.replace('d:','')
			coden=coden[0:].replace(' ','')
			
			value = eval(coden, {}, {**variables, **constable,**array,**listStr,**listInt})
			value=float(value)
			variables[var]=value
		elif 'b:' in var:
			var=var.replace('b:','')
			coden=coden[0:].replace(' ','')
			
			value = eval(coden, {}, {**variables, **constable,**array,**listStr,**listInt})
			value=bool(value)
			variables[var]=value
		elif var in constable:
			err('نام در ثابت ها رزرو شده نام دیگر انتخاب کن')
		else:
			coden=coden[0:].replace(' ','')
			value = eval(coden, {}, {**variables, **constable,**array,**listStr,**listInt})
			variables[var]=value
	
	#تابع ord,chr
	elif code.startswith('Asci(') and code.endswith(')'):
		code = code[5:-1].strip()
		try:
        # بررسی اینکه حتما '=' وجود دارد
			if '=' not in code:
				err("فرمت دستور Asci() اشتباه است. باید به‌صورت Asci(var=^A^) باشد")
				return
			var, char = code.split('=', 1)
			var = var.strip()
			char = char.strip()

        # بررسی نام متغیر
			if var in constable:
				err('نام متغیر از نام ثابت‌ها است و رزرو شده، نام دیگری انتخاب کن')
				return

        # حذف ^ در صورت وجود
			if char.startswith('^') and char.endswith('^'):
				char = char[1:-1]

        # اگر مقدار خودش در متغیرهاست
			if char in variables:
				char = variables[char]

        # تبدیل به عدد ASCII
			if len(char) != 1:
				err("در Asci() فقط یک کاراکتر مجاز است، نه رشته چندحرفی")
				return

			value = ord(char)

        # اگر متغیر قابل نوشتن است
			if var not in ['¿', 'null']:
				variables[var] = value
			else:
				print(value)

		except Exception as e:
			err(f"نحو دستور اشتباه است Asci(): {e}")
			
	elif code.startswith('Char(') and code.endswith(')'):
		code = code[5:-1].strip()
		try:
        # بررسی اینکه حتما '=' وجود دارد
			if '=' not in code:
				err("باید از = در داخل پرانتز استفاده کنی مثل این a=^C^")
				return
			var, char = code.split('=', 1)
			var = var.strip()
			char = char.strip()

        # بررسی نام متغیر
			if var in constable:
				err('نام متغیر از نام ثابت‌ها است و رزرو شده، نام دیگری انتخاب کن')
				return

        # حذف ^ در صورت وجود
			if char.startswith('^') and char.endswith('^'):
				char = char[1:-1]
				char=int(char)

        # اگر مقدار خودش در متغیرهاست
			if char in variables:
				char = variables[char]

        # تبدیل به عدد ASCII
			

			value = chr(char)

        # اگر متغیر قابل نوشتن است
			if var not in ['¿', 'null']:
				variables[var] = value
			else:
				print(value)

		except Exception as e:
			err(f"نحو دستور Char(x=^x^) اشتباهه")
	#تعریف آرایه
	# تعریف آرایه
	elif code.startswith('arr') and '=' in code:
		try:
			name_part, value_part = code.split('=', 1)
			name = name_part.replace('arr', '', 1).strip()  # فقط اولین 'arr' حذف شود

			if not name:
				err("نام آرایه نمی‌تواند خالی باشد")
				return

			if not value_part.strip():
				err("مقدار آرایه مشخص نشده است")
				return

			value = value_part.strip()

			# آرایه عددی → i{1, 2, 3}
			if value.startswith('i{') and value.endswith('}'):
				items_str = value[2:-1]
				if not items_str.strip():
					array[name] = []
				else:
					items = [item.strip() for item in items_str.split(',')]
					try:
						array[name] = [int(x) for x in items if x]  # نادیده گرفتن موارد خالی
					except ValueError:
						err(f"همه مقادیر در آرایه‌ی '{name}' باید عدد صحیح باشند")
						return

			# آرایه رشته‌ای → s{ali, ^reza, "sara"}
			elif value.startswith('s{') and value.endswith('}'):
				items_str = value[2:-1]
				if not items_str.strip():
					array[name] = []
				else:
					items = [item.strip() for item in items_str.split(',')]
					# حذف کوتیشن‌های اطراف و علامت ^ اگر وجود داشت (برای حالت خاص شما)
					cleaned = []
					for s in items:
						if not s:
							continue
						s = s.strip('"').strip("'")
						if s.startswith('^'):
							s = s[1:]
						cleaned.append(s)
					array[name] = cleaned

			# آرایه محاسباتی → m{1+2, x*3, arr1[0]}
			elif value.startswith('m{') and value.endswith('}'):
				items_str = value[2:-1]
				if not items_str.strip():
					array[name] = []
				else:
					items = [item.strip() for item in items_str.split(',') if item.strip()]
					result = []
					for expr in items:
						try:
							val = eval(expr, {"__builtins__": {}}, {**variables, **constable, **array,**listStr,**listInt})
							result.append(val)
						except Exception as e:
							err(f"خطا در محاسبه عبارت '{expr}' در آرایه '{name}': {e}")
							return
					array[name] = result

			else:
				err("فرمت تعریف آرایه نادرست است. از یکی از قالب‌های زیر استفاده کنید:\n"
				    "   arr name = i{1, 2, 3}\n"
				    "   arr name = s{ali, reza, \"sara\"}\n"
				    "   arr name = m{1+5, x*2, oldarr[0]}")
				return

		except ValueError:
			err("ساختار دستور arr نادرست است (علامت = پیدا نشد یا چندتا بود)")
		except Exception as e:
			err(f"خطای غیرمنتظره در تعریف آرایه: {e}")
		return
	###
# دسترسی به آرایه - فقط وقتی دقیقاً فرمت arr[index] یا arr[^value^] باشه
	elif re.match(r'^\s*[a-zA-Z_]\w*\s*\[[^\[\]]*\]\s*$', code.strip()):
		try:
			

			# پارس دقیق: فقط نام_آرایه[محتوا]
			match = re.match(r'^\s*([a-zA-Z_]\w*)\s*\[\s*(.+?)\s*\]$', code.strip())
			if not match:
				err("سینتکس دسترسی به آرایه نامعتبر است")
				return

			arr_name = match.group(1)
			index_part = match.group(2).strip()

			if arr_name not in array:
				err(f"آرایه '{arr_name}' تعریف نشده است")
				return

			arr = array[arr_name]

			# حالت جستجوی رشته‌ای با ^...^
			if index_part.startswith('^') and index_part.endswith('^'):
				search_val = index_part[1:-1].strip()
				str_items = [str(item) for item in arr]
				if search_val in str_items:
					print(str_items.index(search_val))
				else:
					err(f"مقدار '^{search_val}^' در آرایه '{arr_name}' پیدا نشد")

			# حالت جستجو فقط با ^ در ابتدا (مثل [^reza])
			elif index_part.startswith('^'):
				search_val = index_part[1:].strip().strip('"').strip("'")
				str_items = [str(item) for item in arr]
				if search_val in str_items:
					print(str_items.index(search_val))
				else:
					err(f"مقدار '^{search_val}' در آرایه '{arr_name}' پیدا نشد")

			# حالت اندیس عددی یا محاسبه‌شده
			else:
				try:
					# اول سعی کن مستقیم به عدد تبدیل کنی
					index = int(index_part)
				except ValueError:
					# اگر نشد، از p_dim استفاده کن (مثل x+1 یا name=>[0:1])
					try:
						index = int(eval(index_part, {}, {**variables, **constable,**array,**listStr,**listInt}))
					except:
						err(f"اندیس نامعتبر است: {index_part}")
						return

				# بررسی محدوده اندیس (پشتیبانی از اندیس منفی)
				if index < -len(arr) or index >= len(arr):
					err(f"اندیس {index} خارج از محدوده آرایه '{arr_name}' (اندازه: {len(arr)})")
				else:
					print(arr[index])

		except Exception as e:
			err(f"خطا در دسترسی به آرایه: {e}")
###

	# --- تشخیص fun(...) {...} با آرگومان typed و نامحدود ---
	elif code.startswith('*pop') and '<>' in code:
		print('pop(popcorn)زبان برنامه نویسی در حال توسعه نام نویسنده:ابوالفضل محمدی')
		
	elif code.startswith("file") and code[4] == "(" and code[-1] == ")":
		inside = code[5:-1].strip()
		try:
			parts = [p.strip() for p in inside.split(',')]
			cmd = parts[0].lower()
        
        # open فایل (فعلاً فقط برای ثبت نام فایل)
			if cmd == "open" and len(parts) == 2:
				filename = parts[1].strip('^"')
				files[filename] = open(filename, 'a+', encoding='utf-8')
        
        # write به فایل
			elif cmd == "write" and len(parts) == 3:
				filename = parts[1].strip('^"')
				text = parts[2].strip('^"')
				if filename in files:
					files[filename].write(text)
					files[filename].flush()
				else:
					err(f"فایل {filename} باز نشده")
        
        # append به فایل
			elif cmd == "append" and len(parts) == 3:
				filename = parts[1].strip('^"')
				text = parts[2].strip('^"')
				with open(filename, 'a', encoding='utf-8') as f:
					f.write(text)
        
        # read از فایل
			elif cmd == "read" and len(parts) == 2:
				filename = parts[1].strip('^"')
				if filename in files:
					files[filename].seek(0)
					print(files[filename].read())
				else:
					try:
						with open(filename, 'r', encoding='utf-8') as f:
							print(f.read())
					except Exception as e:
						err(f"خطا در خواندن فایل {filename}: {e}")
        
        # close فایل
			elif cmd == "close" and len(parts) == 2:
				filename = parts[1].strip('^"')
				if filename in files:
					files[filename].close()
					del files[filename]
				else:
					err(f"فایل {filename} باز نشده")
        
        # delete فایل
			elif cmd == "delete" and len(parts) == 2:
				import os
				filename = parts[1].strip('^"')
				try:
					os.remove(filename)
				except Exception as e:
					err(f"خطا در حذف فایل {filename}: {e}")
        
			else:
				err("فرمت دستور file اشتباه است یا فرمان ناشناخته")
		except Exception as e:
			err(f"خطا در دستور file: {e}")

	elif code.startswith("math") and code[4] == "(" and code[-1] == ")":
		import math as m
		import random as r
		try:
			inside = code[5:-1].strip()
			parts = [p.strip() for p in inside.split(',')]
			func = parts[0].lower()
        
        # sqrt
			if func == "sqrt" and len(parts) == 2:
				val = float(eval(parts[1], {}, {**variables, **constable,**array,**listStr,**listInt}))
				print(m.sqrt(val))
        
        # pow
			elif func == "pow" and len(parts) == 3:
				base = float(eval(parts[1], {}, {**variables, **constable,**array,**listStr,**listInt}))
				exp = float(eval(parts[2], {}, {**variables, **constable,**array,**listStr,**listInt}))
				print(m.pow(base, exp))
        
        # sin, cos, tan (در رادیان)
			elif func in ["sin","cos","tan"] and len(parts) == 2:
				val = float(eval(parts[1], {}, {**variables, **constable,**array,**listStr,**listInt}))
				if func=="sin": print(m.sin(val))
				elif func=="cos": print(m.cos(val))
				elif func=="tan": print(m.tan(val))
        
        # log
			elif func == "log" and len(parts) >= 2:
				val = float(eval(parts[1], {}, {**variables, **constable,**array,**listStr,**listInt}))
				base = float(eval(parts[2], {}, {**variables, **constable,**array,**listStr,**listInt})) if len(parts)==3 else 10
				print(m.log(val, base))
        
        # random
			elif func == "randint" and len(parts) == 3:
				start = int(eval(parts[1], {}, {**variables, **constable,**array,**listStr,**listInt}))
				end = int(eval(parts[2], {}, {**variables, **constable,**array,**listStr,**listInt}))
				print(r.randint(start,end))
        
        # random float بین 0 تا 1
			elif func == "rand" and len(parts)==1:
				print(r.random())
        
			else:
				err(f"math function ناشناخته یا پارامتر نادرست: {func}")
    
		except Exception as e:
			err(f"خطا در دستور math: {e}")
			
	elif code.startswith("beep(") and code.endswith(")"):
		try:
			inside = code[5:-1].strip()
			parts = [p.strip() for p in inside.split(',')]
			
			if len(parts) < 2:
				err("beep(freq,duration) حداقل دو پارامتر می‌خواد")
				return

			# فرکانس
			freq = float(eval(parts[0], {}, {**variables, **constable, **array,**listStr,**listInt}))
			if freq <= 0: freq = 440

			# مدت زمان (میلی‌ثانیه)
			duration_ms = int(eval(parts[1], {}, {**variables, **constable, **array,**listStr,**listInt}))
			if duration_ms < 10: duration_ms = 10

			# ولوم اختیاری (0–100)
			volume = 80
			if len(parts) >= 3:
				volume = max(0, min(100, int(eval(parts[2], {}, {**variables, **constable, **array,**listStr,**listInt}))))

			import os
			import time

			# ویندوز — صدای واقعی و شفاف
			if os.name == 'nt':  # ویندوز
				import winsound
				freq = int(freq)
				freq = max(37, min(32767, freq))  # محدوده مجاز ویندوز
				winsound.Beep(freq, duration_ms)

			# لینوکس و مک — بوق سیستم
			else:
				# روی لینوکس: بوق واقعی از اسپیکر PC
				if os.uname().sysname == 'Linux':
					try:
						# روش اول: استفاده از pcspkr (اگر ماژول لود شده باشه)
						with open('/dev/console', 'w') as console:
							console.write('\a')
						# یا استفاده از beep مستقیم (اگر نصب باشه)
						os.system(f'beep -f {freq} -l {duration_ms//10} 2>/dev/null || true')
					except:
						pass

				# روش استاندارد برای همه سیستم‌ها: ASCII Bell
				cycles = max(1, int(freq * duration_ms / 1000))
				delay = duration_ms / 1000.0 / max(1, cycles)

				for _ in range(cycles):
					print('\a', end='')
					import sys
					sys.stdout.flush()
					time.sleep(delay)

		except Exception as e:
			err(f"خطا در beep(): {e}")
	###
	elif code.lower().startswith("cls") and (code.lower() == "cls" or (code.startswith("cls(") and code.endswith(")"))):
		try:
			import os
			import sys

			# تشخیص محیط
			is_android = False
			try:
				if 'ANDROID_ROOT' in os.environ or 'com.termux' in os.environ.get('PREFIX', ''):
					is_android = True
			except:
				pass

			is_windows = os.name == "nt"

			# روش اصلی: استفاده از ANSI escape codes (روی همه جا کار می‌کنه!)
			if not is_windows or is_android:
				# این کد روی لینوکس، مک، اندروید، Pydroid 3، Termux — همه جا کار می‌کنه
				sys.stdout.write('\033[H\033[J\033[3J')
				sys.stdout.flush()
			else:
				# ویندوز: از دستور cls استفاده کن
				os.system('cls')

			# اگر پارامتر داده شده بود (مثلاً cls(reset)) — فقط برای آینده
			if code.startswith("cls("):
				arg = code[4:-1].strip().lower()
				if arg in ["reset", "default", "clean"]:
					# برگرداندن رنگ به حالت عادی (برای همه سیستم‌ها)
					sys.stdout.write('\033[0m')
					sys.stdout.flush()

		except Exception as e:
			pass  # هیچ خطایی نشون نده، فقط صفحه رو پاک کنه
###
	elif code.startswith("color(") and code.endswith(")"):
		try:
			inside = code[6:-1].strip()
			if not inside:
				return
			parts = [p.strip().lower() for p in inside.split(",")]

			# فقط 1 یا 2 مقدار
			if len(parts) > 2 or len(parts) == 0:
				return

			# رنگ‌های استاندارد (دقیق و بدون اشتباه)
			colors = {
				"black": 0, "red": 1, "green": 2, "yellow": 3,
				"blue": 4, "magenta": 5, "cyan": 6, "white": 7,
				"gray": 8, "lred": 9, "lgreen": 10, "lyellow": 11,
				"lblue": 12, "lmagenta": 13, "lcyan": 14, "lwhite": 15
			}

			text = parts[0]
			back = parts[1] if len(parts) == 2 else None

			if text not in colors:
				return  # رنگ اشتباه = هیچ کاری نکن

			import os
			is_win = os.name == "nt"

			if is_win:
				# ویندوز: کد 16تایی
				if back and back in colors:
					code = f"{colors[back]:x}{colors[text]:x}"
				else:
					code = f"{colors[text]:x}"
				os.system(f"color {code}")
			else:
				# ANSI برای همه بقیه (لینوکس، مک، اندروید)
				t = colors[text]
				if t >= 8:
					t += 82  # 90–97 برای رنگ روشن
				else:
					t += 30   # 30–37 برای رنگ معمولی

				b = ""
				if back and back in colors:
					bb = colors[back]
					if bb >= 8:
						b = f";{bb + 92}"   # 100–107
					else:
						b = f";{bb + 40}"   # 40–47

				print(f"\033[{t}{b}m", end="")

		except:
			pass
			
###
	elif code.startswith("key(") and code.endswith(")"):
		try:
			inside = code[4:-1].strip()
			if not inside:
				return

			# جدا کردن نام متغیر و تایم‌اوت (اختیاری)
			timeout = None  # یعنی بی‌نهایت صبر کن
			if ',' in inside:
				varname, timeout_str = [p.strip() for p in inside.split(',', 1)]
				timeout = float(eval(timeout_str, {}, {**variables, **constable, **array,**listStr,**listInt})) / 1000.0
			else:
				varname = inside

			if not varname or varname in constable:
				return

			import os
			import sys
			import select
			import time

			# کلیدهای خاص
			keys = {
				'\x1b[A': 'up',    '\x1bOA': 'up',
				'\x1b[B': 'down',  '\x1bOB': 'down',
				'\x1b[C': 'right', '\x1bOC': 'right',
				'\x1b[D': 'left',  '\x1bOD': 'left',
				'\x7f': 'backspace', '\x08': 'backspace',
				'\r': 'enter', '\n': 'enter',
				'\x1b': 'esc', ' ': 'space'
			}

			result = "¿"

			if os.name == 'nt':  # ویندوز
				import msvcrt
				if timeout is None:
					while not msvcrt.kbhit():
						time.sleep(0.01)
					ch = msvcrt.getch()
					if ch in (b'\x00', b'\xe0'):
						ch += msvcrt.getch()
					result = keys.get(ch.decode('utf-8', 'ignore'), ch.decode('utf-8', 'ignore').lower())
				else:
					start = time.time()
					while time.time() - start < timeout:
						if msvcrt.kbhit():
							ch = msvcrt.getch()
							if ch in (b'\x00', b'\xe0'):
								ch += msvcrt.getch()
							result = keys.get(ch.decode('utf-8', 'ignore'), ch.decode('utf-8', 'ignore').lower())
							break
						time.sleep(0.01)

			else:  # اندروید، لینوکس، مک
				if timeout is None:
					# بی‌نهایت صبر کن تا کلیدی فشرده بشه
					while True:
						r, _, _ = select.select([sys.stdin], [], [], 1.0)
						if r:
							break
				else:
					r, _, _ = select.select([sys.stdin], [], [], timeout)
					if not r:
						variables[varname] = "¿"
						return

				# حالا کلید رو بخون
				ch = sys.stdin.read(1)
				if ch == '\x1b':
					if select.select([sys.stdin], [], [], 0.02)[0]:
						ch += sys.stdin.read(10)
				result = keys.get(ch, ch.lower())

			# ذخیره نتیجه در متغیر
			variables[varname] = result

		except:
			pass
###
	# داخل run_line()، بعد از بقیه elif ها اضافه کن:

# ──────────────────────────────────────────────────────────────
    # دستور sys(^دستور سیستم^) – اجرای دستورات شل/CMD به صورت قوی و امن
    # مثال‌ها:
    #   sys(dir)
    #   sys(ls -la)
    #   sys(pip install requests)
    #   sys(git status)
    #   sys(^echo سلام دنیا^)
    # ──────────────────────────────────────────────────────────'────
	else:
		err('دستور ناشناخته')
		
#بخش شرط آزمایشی

# --- مثال تست ---
#run_line('con$pi=3')
#run_line('inp(name,^input_\\nname:^)')
#run_line('inp(age,^input\\sage:^)')
#run_line('inp(num1,i^input\\snumber:^)')
#run_line('var num2=6')
#run_line('int num3=6')
#run_line('put(^Name\\s:^,name,^Age_:^,age)')
#run_line('put(~num1+num2~)')
#run_line('put(pi,^_^,name)')
#run_line('put(name,^\\s^,age)')
#run_line('inp(id,f^input\\sid_{name}:^)')
#run_line('put(f^hello\\t{name}\\t{id}^)')
#run_line('inp(n,i#input\\sn:#)')
#run_line('inp(do,d#input\\sdo:#)') 
#run_line('inp(bo,b#input\\sbo:#)')
#run_line('put(f^{n}\\n{do}\\n{bo}^)')
#run_line('int nn=~num2+num3~')
#run_line('dou r1=~3.14*3*3~')
#run_line('put(f^{nn}\\n{r1}^)')
#run_line('bol bool=~num3>num2~')
#run_line('put(bool)')
#run_line('inp(n1,i^Enter_n1:^)')
#run_line('inp(n2,i^Enter_n2:^)')
#run_line('int r=~n1+n2~')
#run_line('put($^Result\\n{n1}+{n2}={r}^)')

#یه بخش تست آزمایشی
def run_file(filename):
	print('_____________    __     ___                   ___')
	print('|  |      |  |   |  |     |    \                /     |')
	print('|  |      |  |   |  |     |      \            /       |')
	print('|  |      |  |   |  |     |   |\   \       /   /|    | ')
	print('|  |      |  |   |  |     |   |  \   \   /   /  |    |')
	print('|  |      |  |   |  |     |   |    \   V   /    |    |')
	print('■■■■■■■■■■■■■■■')
	try:
		print('[Running code file:', filename, 'version interpreter is:', version, ']')
		with open(filename, 'r', encoding='utf-8') as f:
			lines = [line.rstrip('\n') for line in f]

		i = 0
		while i < len(lines):
			line = lines[i].strip().replace(' ','')
			if not line:
				i += 1
				continue
			global current_line_number
			current_line_number =i+1

            # --- LOOP (مثل while) ---
			if line.startswith('LOOP(') and '>>' in line:
				cond_part, rest = line.split('>>', 1)
				condition = cond_part[5:-1].strip()  # استخراج شرط داخل LOOP(...)
				block, new_i = run_block(lines, i)
				while True:
					try:
						cond_result = eval(condition, {}, {**variables, **constable,**listStr,**listInt})
					except Exception as e:
						err(f"EvalErr in LOOP condition: {e}")
						break
					if not cond_result:
						break
				i = new_i
				continue
			elif line.startswith('IF(') and '>>' in line:
				chain_executed = False
				while i < len(lines):
					line = lines[i].strip()

                    # --- IF ---
					if line.startswith('IF(') and '>>' in line and not chain_executed:
						cond_part, rest = line.split('>>', 1)
						condition = cond_part[3:-1].strip()
						try:
							cond_result = eval(condition, {}, {**variables, **constable,**array,**listStr,**listInt})
						except Exception as e:
							err(f"EvalErr in IF condition: {e}")
							cond_result = False

						block, new_i = run_block(lines, i)
						if cond_result:
							run_block_lines(block)
							chain_executed = True
						i = new_i
						continue

                    # --- ELSEIF ---
					elif line.startswith('ELSEIF(') and '>>' in line:
						if chain_executed:
							block, new_i = run_block(lines, i)
							i = new_i
							continue
						cond_part, rest = line.split('>>', 1)
						condition = cond_part[7:-1].strip()
						try:
							cond_result = eval(condition, {}, {**variables, **constable,**array,**listStr,**listInt})
						except Exception as e:
							err(f"EvalErr in ELSEIF condition: {e}")
							cond_result = False
						block, new_i = run_block(lines, i)
						if cond_result:
							run_block_lines(block)
							chain_executed = True
						i = new_i
						continue

                    # --- ELSE ---
					elif line.startswith('ELSE') and line.endswith('{'):
						block, new_i = run_block(lines, i)
						if not chain_executed:
							run_block_lines(block)
						i = new_i
						break
					else:
						break
				continue


			else:
				run_line(line)
				i += 1

	except FileNotFoundError:
		err(f"File not found: {filename}")

def run_block(lines, start_index):
    """
    استخراج بلوک کد از { ... } (حتی تو در تو)
    خروجی: (لیست خطوط داخل بلوک، اندیس خط بعد از بلوک)
    """
    depth = 0
    block_lines = []
    i = start_index + 1  # از خط بعد از if شروع کن

    while i < len(lines):
        line = lines[i].strip()

        if line.endswith('{'):
            depth += 1
            sub_block, new_i = run_block(lines, i)
            block_lines.append({'type': 'block', 'lines': sub_block})
            i = new_i
            continue

        elif line == '}':
            if depth == 0:
                return block_lines, i + 1
            else:
                depth -= 1

        else:
            block_lines.append(line)

        i += 1

    err("بلوک بسته نشده")
    return block_lines, i


def run_block_lines(block):
    for item in block:
        if isinstance(item, dict) and item.get('type') == 'block':
            run_block_lines(item['lines'])
        else:
            run_line(item)

        
if __name__ == "__main__":
    import os
    if os.path.exists("program.pop"):
        run_file("program.pop")
    else:
        print("فایل program.pop پیدا نشد")
