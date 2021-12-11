const btnDelete= document.querySelectorAll('.btn-delete');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to delete it?')){
        e.preventDefault();
      }
    });
  })
}
/* Modificacion del original en postingcode.com
     * Agregado el control de variable cedulaValida y controlando ced.length a menor de 11 
     * para los casos de cédulas sin guiones
     *
     * La cedula utilizada ES una cedula valida y asignada al ciudadano gerente de este script
     * Modificación por Victor Abreu | www.vicabreu.com
     * Nombre del archivo: ValidaCedulaDominicana.html
     */ 
    
var cedulaValida = "00116454281";
var cedulaNoValida = "40226883979";

/* Validación de número de cédula dominicana
 * con longitud de 11 caracteres numéricos o 13 caracteres incluyendo los dos guiones de presentación
 * ejemplo sin guiones 00116454281, ejemplo con guiones 001-1645428-1
 * el retorno es 1 para el caso de cédula válida y 0 para la no válida
 */
function valida_cedula(ced) {  
    var c = ced.replace(/-/g,'');  
    var cedula = c.substr(0, c.length - 1);  
    var verificador = c.substr(c.length - 1, 1);  
    var suma = 0;  
    var cedulaValida = 0;
    if(ced.length < 11) { return false; }  
    for (i=0; i < cedula.length; i++) {  
        mod = "";  
         if((i % 2) == 0){mod = 1} else {mod = 2}  
         res = cedula.substr(i,1) * mod;  
         if (res > 9) {  
              res = res.toString();  
              uno = res.substr(0,1);  
              dos = res.substr(1,1);  
              res = eval(uno) + eval(dos);  
         }  
         suma += eval(res);  
    }  
    el_numero = (10 - (suma % 10)) % 10;  
    if (el_numero == verificador && cedula.substr(0,3) != "000") {  
      cedulaValida = 1;
    }  
    else   {  
     cedulaValida = 0;
    }  
    return cedulaValida;
}

function myFunction() {
var x = document.getElementById("myText").value;
if(valida_cedula(x)==false){
    alert('La cedula no es validad'); }

else{return true;}

return false;
}

$('.cedula').mask('000-0000000-0');

$('.telefono').mask('000-000-0000');


document.addEventListener('DOMContentLoaded', function() {
  applyInputMask('elinput', '0--0*0 000_000');
});

