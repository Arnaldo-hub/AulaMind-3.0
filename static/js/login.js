/*
==========================================================
AulaMind Enterprise 3.0
Login
==========================================================
*/

document.addEventListener(

    "DOMContentLoaded",

    function(){

        const form = document.querySelector("form");

        if(!form){

            return;

        }

        form.addEventListener(

            "submit",

            function(e){

                const password = document.querySelector(

                    'input[name="password"]'

                );

                const confirm = document.querySelector(

                    'input[name="confirm_password"]'

                );

                if(confirm){

                    if(password.value !== confirm.value){

                        e.preventDefault();

                        alert(

                            "Las contraseñas no coinciden."

                        );

                        confirm.focus();

                        return;

                    }

                }

                if(password.value.length < 8){

                    e.preventDefault();

                    alert(

                        "La contraseña debe tener al menos 8 caracteres."

                    );

                    password.focus();

                    return;

                }

            }

        );

    }

);