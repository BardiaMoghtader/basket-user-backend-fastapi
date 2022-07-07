htmlStart = '''
<!DOCTYPE html>   
<html>   
<head>  
<meta name="viewport" content="width=device-width, initial-scale=1">  
<title> Login Page </title> 
</head>    
<body> 
'''

HtmlEnd = '''
</body>     
</html>
'''

rootResponse = htmlStart + \
'''
<style>
a#login-button.button.logout.login.w-button {
  position:relative;
  box-sizing: border-box;
  background-color: #66ffcc;
  background-image: none;
  border-radius: 25px;
  border-width: 0;
  bottom: auto;
  box-sizing: border-box;
  color: #253858;
  cursor: pointer;
  display: block;
  flex: 1;
  float: right;
  font-family: Poppins, sans-serif;
  font-size: 12px;
  left: auto;
  letter-spacing: 1px;
  line-height: 19px;
  margin-left: -15px;
  margin-right: 15px;
  margin-top: 15px;
  padding: 5px 15px;
  /*position: absolute;*/
  right: 0;
  text-align: center;
  text-decoration: none;
  top: 0;
  transition: background-color 150ms;
  z-index: 30;
}
 
a#login-button.button.logout.login.w-button:active {
  outline: 0;
}
 
a#login-button.button.logout.login.w-button:hover {
  background-color: #2ac28f;
  font-weight: 400;
  outline: 0;
}
 
</style>
<a id="login-button" ms-hide-element="true" href="/login" class="button logout login w-button">Login</a>
<a id="login-button" ms-hide-element="true" href="/signup/" class="button logout login w-button">SignUp</a>
''' \
+ HtmlEnd

loginResponse = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" method="POST" action="/login" >
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
              Username
            </label>
            <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" name="username" type="text">
          </div>
          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
              Password
            </label>
            <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" id="password" name="password" type="password">
          </div>
          <div class="flex items-center justify-between">
            <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
              Sign In
            </button>
          </div>
        </form>
      </div>
</body>
</html> 
'''
