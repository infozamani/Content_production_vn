import google.generativeai as genai

# کلید API را اینجا قرار دهید
genai.configure(api_key="AIzaSyDBnqIGnrhcXoXEXU9fqXXW1NUAUMC7Owc")

# مدل را انتخاب کنید
model = genai.GenerativeModel('gemini-2.5-flash')

# درخواست بفرستید
response = model.generate_content("سلام، چطوری؟")
print(response.text)