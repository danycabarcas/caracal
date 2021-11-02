function mostrarPassword(){
    let campoTipo = document.getElementById("contraseña");
    campoTipo.type = "text";
    //campoTipo.type == "password" ? campoTipo.type = "text" : campoTipo.type = "password";
    // if(tipo.type == "password"){
    //     tipo.type = "text";
    // }
}
function ocultarPassword(){
    let campoTipo = document.getElementById("contraseña");
    campoTipo.type = "password";
    //campoTipo.type == "text" ? campoTipo.type = "password" : campoTipo.type = "text";
    // if(tipo.type == "text"){
    //     tipo.type = "password";
    // }
}