function displayingDiv(element) {
    let el = document.getElementById(element);
    if (el.style.display == "none") {
        el.style.display = "block"
    }
    else {
        el.style.display = "none"
    }
}