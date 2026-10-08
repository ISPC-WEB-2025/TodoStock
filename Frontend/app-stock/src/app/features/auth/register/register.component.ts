import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { validadorPassword } from './register.validator';
import { UserAuthService } from '../../../core/services/user-auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent {
  // Inyección de servicios
  private userAuthService = inject(UserAuthService);
  private router = inject(Router);

  // Texto localizable
  // TODO(TMF): AGREGAR MAS STRINGS QUE SE PUEDAN LOCALIZAR/SEAN TRADUCIBLES
  readonly creaTuCuenta: string = '¡Creá tu cuenta!';
  readonly registroError: string =
    'Hay campos que son inválidos. ¡Por favor revisalos antes de enviar el formulario!';
  readonly errorDesconocido: string = 'Error desconocido.';
  readonly nombreVacio: string =
    'Ingresá un nombre de usuario con 6 o más caracteres.';
  readonly emailVacio: string = 'Ingresá un correo electrónico.';
  readonly emailInvalido: string =
    'Los datos para el correo electrónico no son válidos.';
  readonly passwordVacio: string = 'Ingresá una contraseña.';
  readonly passwordInvalidoOwasp: string =
    'La contraseña debe tener al menos 9 caracteres, incluyendo letras, números y un símbolo especial (sin espacios).';
  readonly passwordNoCoincide: string = 'Las contraseñas no coinciden.';
  readonly dniInvalido: string = 'El número de documento tiene que ser único y tener entre 7 u 8 dígitos.';
  readonly fdnInvalido: string = 'Ingresá una fecha de nacimiento.';
  readonly mensajeExito: string =
    '¡Cuenta creada con éxito! Tu cuenta está pendiente de aprobación por el administrador antes de poder iniciar sesión.';
  // URI de imagenes
  readonly imagenURI: string = 'assets/deposito.png';
  readonly cajaURI: string = 'assets/ToDoLogosf.png';

  // Registro de formularios
  public registerForm!: FormGroup;
  public registerErrored: boolean = false;
  public backendError: string | null = null;
  public registroExitoso: boolean = false;
  protected esconderPassword: boolean = true;

  // Regex OWASP: >=9 caracteres, >=1 letra, >=1 número, >=1 símbolo, sin espacios
  private readonly owaspPasswordPattern = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[^a-zA-Z0-9\s])\S{9,}$/;

  constructor(private formBuilder: FormBuilder) {
    this.registerForm = this.formBuilder.group(
      {
        nombre: ['', [Validators.required, Validators.minLength(6)], []],
        email: ['', [Validators.required, Validators.pattern(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)], []],
        dni: ['', [Validators.required, Validators.pattern(/^\d{7,8}$/)], []],
        fdn: ['', [Validators.required], []],
        password: ['', [Validators.required, Validators.pattern(this.owaspPasswordPattern)], []],
        confirm_password: [
          '',
          [Validators.required],
          [],
        ],
      },
      {
        validators: [validadorPassword('password', 'confirm_password')],
      },
    );
  }

  // Getters
  get nombre() {
    return this.registerForm.get('nombre');
  }

  get email() {
    return this.registerForm.get('email');
  }

  get password() {
    return this.registerForm.get('password');
  }

  get c_password() {
    return this.registerForm.get('confirm_password');
  }

  get dni() {
    return this.registerForm.get('dni');
  }

  get fdn() {
    return this.registerForm.get('fdn');  // Fecha De Nacimiento
  }

  // Manejo de formulario
  public onEnviar(event: Event) {
    event.preventDefault(); // Previene que el navegador haga su trabajo por defecto, ahora lo manejamos desde acá

    this.backendError = null;

    if (this.registerForm.valid) {
      const registerData = this.registerForm.value;

      const nombre: string = registerData.nombre;
      const email: string = registerData.email;
      const dni: number = registerData.dni;
      const fdn: any = registerData.fdn;
      const password: string = registerData.password;

      this.userAuthService.registrar(nombre, email, dni, fdn, password).subscribe({
        next: () => {
          console.log("¡Usuario creado con exito!");
          this.backendError = null;
          this.registroExitoso = true;
          this.registerErrored = false;
          setTimeout(() => this.router.navigate(['/login']), 4000);
        },
        error: (error: any) => {
          console.error("¡Error al registrar usuario!", error);
          this.registroExitoso = false;
          this.registerErrored = true;
          if (error.error) {
            if (typeof error.error === 'string') {
              this.backendError = error.error;
            } else if (error.error.error) {
              this.backendError = error.error.error;
            } else if (error.error.detail) {
              this.backendError = error.error.detail;
            } else if (typeof error.error === 'object') {
              const firstKey = Object.keys(error.error)[0];
              if (firstKey && Array.isArray(error.error[firstKey])) {
                this.backendError = `${firstKey}: ${error.error[firstKey].join(', ')}`;
              } else if (firstKey && typeof error.error[firstKey] === 'string') {
                this.backendError = `${firstKey}: ${error.error[firstKey]}`;
              } else {
                this.backendError = 'Error al registrar usuario. Verificá los datos ingresados.';
              }
            } else {
              this.backendError = 'Error al registrar usuario.';
            }
          } else {
            this.backendError = 'No se pudo conectar con el servidor.';
          }
        },
      });
    } else {
      this.registerErrored = true;
      this.registerForm.markAllAsTouched();
    }
  }

  // Funcion para alternar la vista de contraseñas al clickear en el ojo
  public alternarVisibilidadPassword() {
    this.esconderPassword = !this.esconderPassword;
  }
}
