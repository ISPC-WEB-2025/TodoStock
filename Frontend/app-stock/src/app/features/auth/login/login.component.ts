import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
  FormsModule,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { UserAuthService } from '../../../core/services/user-auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  // 1. Inyección de dependencias usando inject() en lugar de constructor tradicional
  private userAuthService = inject(UserAuthService);
  private formBuilder = inject(FormBuilder);
  private router = inject(Router);

  // Texto localizable
  // TODO(TMF): AGREGAR MAS STRINGS QUE SE PUEDAN LOCALIZAR/SEAN TRADUCIBLES
  readonly mensajeBienvenida: string = '¡Bienvenido a ToDo Stock!';
  readonly emailInvalido: string = 'Por favor ingresá tu correo electrónico';
  readonly passwordNoExiste: string = 'Por favor ingresá  tu contraseña';
  readonly passwordInvalido: string = 'La contraseña tiene que tener 8 o más caracteres';
  readonly datosIncorrectos: string = 'El nombre o contraseña ingresados son incorrectos';
  readonly cuentaPendiente: string = 'Tu cuenta está pendiente de aprobación. Contactá al administrador.';

  // URI de imagenes
  readonly imagenURI: string = 'assets/deposito.png';

  // LoginForms, para detectar datos cuando se clickea el boton de iniciar sesion, y su estado
  public loginForm!: FormGroup;
  public loginError: Boolean = false;
  public pendienteAprobacion: Boolean = false; // Nuevo estado para usuarios sin rol asignado

  constructor() {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email], []],
      password: ['', [Validators.required], []],
      recordar: ['', []],
    });
  }

  // Getters para que el template pueda ver nuestros datos
  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  get loginErrored(): Boolean {
    return this.loginError;
  }

  public onEnviar(event: Event) {
    event.preventDefault(); // Previene que el navegador haga su trabajo por defecto, ahora lo manejamos desde acá

    this.loginError = false;
    this.pendienteAprobacion = false;

    // Procedemos si todos los datos del formulario estan llenados y son válidos antes de contactar con el backend
    if (this.loginForm.valid) {
      const email = this.loginForm.value.email;
      const password = this.loginForm.value.password;
      const recordar = !!this.loginForm.value.recordar;

      // Llamada asincrónica al backend usando .subscribe()
      this.userAuthService.login(email, password, recordar).subscribe({
        next: (respuesta) => {
          // Si Django devuelve 200 OK, entramos acá
          this.loginError = false;

          // Redirigir según los booleanos que definimos en el backend
          if (respuesta.es_admin) {
            this.router.navigate(['/dashboard']);
          } else if (respuesta.es_empleado) {
            this.router.navigate(['/vendedor']); // Mantenemos la ruta a vendedor
          } else {
            // Fallback por si el usuario no tiene ningún rol asignado
            localStorage.clear(); // limpiamos el token que guardó el el backend por seguridad       
            this.loginError = true;  
            this.pendienteAprobacion = true;
          }
        },
        error: (err) => {
          // Si Django devuelve 401 Unauthorized o 403 Forbidden
          console.error('Error de autenticación', err);
          this.loginError = true;
          if (err.status === 403) {
            this.pendienteAprobacion = true;
          } else {
            this.pendienteAprobacion = false;
          }
        }
      });
    } else {
      // Fallo en login, al menos un campo tiene errores
      this.loginForm.markAllAsTouched();
    }
  }
}