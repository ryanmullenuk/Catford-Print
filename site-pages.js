const toggle=document.querySelector('.menu-toggle');
const navigation=document.querySelector('.main-nav');
if(toggle&&navigation)toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')==='true';toggle.setAttribute('aria-expanded',String(!open));navigation.classList.toggle('open')});
document.querySelectorAll('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
