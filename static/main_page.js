function getCookie(name, json = false) {
    if (!name) {
        return undefined;
    }
    let matches = document.cookie.match(
        new RegExp(
            "(?:^|; )" + name.replace(/([.$?*|{}()\[\]\\\/+^])/g, "\\$1") + "=([^;]*)"
        )
    );
    if (matches) {
        let res = decodeURIComponent(matches[1]);
        if (json) {
            try {
                return JSON.parse(res);
            } catch (e) {
            }
        }
        return res;
    }
    return undefined;
}

function setCookie(name, value, options = {path: "/"}) {
    /*
      Sets a cookie with specified name (str), value (str) & options (dict)
      options keys:
      - path (str) - URL, for which this cookie is available (must be absolute!)
      - domain (str) - domain, for which this cookie is available
      - expires (Date object) - expiration date&time of cookie
      - max-age (int) - cookie lifetime in seconds (alternative for expires option)
      - secure (bool) - if true, cookie will be available only for HTTPS.
                        IT CAN'T BE FALSE
      - samesite (str) - XSRF protection setting.
                         Can be strict or lax
                         Read https://web.dev/samesite-cookies-explained/ for details
      - httpOnly (bool) - if true, cookie won't be available for using in JavaScript
                          IT CAN'T BE FALSE
      */
    if (!name) {
        return;
    }
    options = options || {};
    if (options.expires instanceof Date) {
        options.expires = options.expires.toUTCString();
    }
    if (value instanceof Object) {
        value = JSON.stringify(value);
    }
    let updatedCookie =
        encodeURIComponent(name) + "=" + encodeURIComponent(value);
    for (let optionKey in options) {
        updatedCookie += "; " + optionKey;
        let optionValue = options[optionKey];
        if (optionValue !== true) {
            updatedCookie += "=" + optionValue;
        }
    }
    document.cookie = updatedCookie;
}

function createButtons(name, quantity) {
    let button1 = document.createElement("input");
    button1.setAttribute("type", "button");
    button1.setAttribute("value", "-");
    button1.setAttribute("onclick", "deleteCart('" + name + "')");

    let sp = document.createElement("span");
    sp.setAttribute("id", "q " + name);
    sp.textContent = quantity;

    let button2 = document.createElement("input");
    button2.setAttribute("type", "button");
    button2.setAttribute("value", "+");
    button2.setAttribute("onclick", "addCart('" + name + "')");


    let div = document.createElement("div");
    div.setAttribute("id", "table " + name);
    div.setAttribute("class", "buttons-to-cart");
    div.append(button1);
    div.append(sp);
    div.append(button2);

    let table = document.getElementById("table " + name);
    table.replaceWith(div);
}

function createButton(name) {
    let button1 = document.createElement("input");
    button1.setAttribute("type", "button");
    button1.setAttribute("value", "В корзину");
    button1.setAttribute("onclick", "addCart('" + name + "')");
    let div = document.createElement("div");
    div.setAttribute("id", "table " + name);
    div.setAttribute("class", "buttons-to-cart");
    div.append(button1);

    let table = document.getElementById("table " + name);
    table.replaceWith(div);
}

function deleteCart(name) {
    let cart = getCookie("cart", true) || {};
    if (name in cart) {
        if (cart[name] > 1) {
            cart[name] -= 1;
            document.getElementById("q " + name).textContent = cart[name];
        } else {
            delete cart[name];
            createButton(name);
        }
    }
    let all = Object.values(cart).reduce((a, b) => a + b, 0);
    // document.getElementById("All").textContent = String(all);
    setCookie("cart", cart);
}

function addCart(name) {
    let cart = getCookie("cart", true) || {};
    if (name in cart) {
        cart[name] += 1;
        document.getElementById("q " + name).textContent = cart[name];
    } else {
        cart[name] = 1;
        createButtons(name, 1);
    }
    let all = Object.values(cart).reduce((a, b) => a + b, 0);
    // document.getElementById("All").textContent = String(all);
    setCookie("cart", cart);
}
