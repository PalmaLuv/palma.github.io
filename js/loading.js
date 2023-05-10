window.onload = function () {
  var timeoutId = window.setTimeout(function () {
    document.body.querySelector('loaded');
    document.body.classList.add('loaded_hiding');
  }, 500);

  var headerWrapper = document.querySelector('.header__wrapper');
  if (headerWrapper.complete) {
    window.clearTimeout(timeoutId);
    document.body.classList.add('loaded_hiding');
  } else {
    headerWrapper.addEventListener('load', function () {
      window.clearTimeout(timeoutId);
      document.body.classList.add('loaded_hiding');
    });
  }
}


/*window.onload = function () {
  document.body.classList.add('loaded_hiding');
    
    window.setTimeout(function () {
      document.body.classList.add('loaded');
      document.body.classList.remove('loaded_hiding');
    }, 500);
  }*/

window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-QKPEQZHNJV');
