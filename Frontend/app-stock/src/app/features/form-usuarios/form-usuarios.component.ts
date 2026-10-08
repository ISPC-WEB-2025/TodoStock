import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Role } from '../../core/models/usuario.model';
import { UsuarioService } from '../../core/services/usuario.service';
import { UserAuthService } from '../../core/services/user-auth.service';
import { ModalService } from '../../core/services/modal.service';

@Component({
  selector: 'app-form-usuarios',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './form-usuarios.component.html',
  styleUrl: './form-usuarios.component.css',
})
export class FormUsuariosComponent implements OnInit {
  private fb = inject(FormBuilder);
  private usuarioService = inject(UsuarioService);
  private authService = inject(UserAuthService);
  private router = inject(Router);
  private modalService = inject(ModalService);
  private route = inject(ActivatedRoute);

  esEdicion = false;
  usuarioId: number | null = null;
  esSuperUsuario = false;
  roles: Role[] = [];
  verPassword = false;
  cargando = false;
  errorFormulario = '';

  usuarioForm: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2)]],
    dni: ['', [Validators.required, Validators.pattern('^[0-9]{7,8}$')]],
    email: ['', [Validators.required, Validators.email]],
    fecha_nacimiento: ['', Validators.required],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(9),
        Validators.pattern(/^(?=.*[a-zA-Z])(?=.*\d)(?=.*[^a-zA-Z\d\s])\S+$/),
      ],
    ],
    rol: ['', Validators.required],
  });

  ngOnInit(): void {
    this.esSuperUsuario = this.authService.isSuperUser();
    this.cargarRoles();
    this.authService.obtenerPerfilActual().subscribe({
      next: () => {
        this.esSuperUsuario = this.authService.isSuperUser();
        this.cargarRoles();
      },
    });

    this.route.params.subscribe((params) => {
      if (params['id']) {
        this.esEdicion = true;
        this.usuarioId = Number(params['id']);

        // En modo edición: contraseña no requerida y email de solo lectura
        this.usuarioForm.get('password')?.clearValidators();
        this.usuarioForm.get('password')?.updateValueAndValidity();
        this.usuarioForm.get('email')?.disable();

        this.cargarUsuario(this.usuarioId);
      }
    });
  }

  cargarRoles(): void {
    this.usuarioService.getRoles().subscribe({
      next: (roles) => {
        this.roles = this.esSuperUsuario
          ? roles
          : roles.filter((r) => r.nombre.toUpperCase() !== 'ADMINISTRADOR');
      },
      error: (err) => {
        console.warn('Error al cargar roles de la API, usando fallback:', err);
        const respaldo: Role[] = [
          { id: 1, nombre: 'ADMINISTRADOR', descripcion: 'Control total' },
          { id: 2, nombre: 'VENTAS', descripcion: 'Ventas y catálogo' },
          { id: 3, nombre: 'DEPOSITO', descripcion: 'Gestión de stock' },
        ];
        this.roles = this.esSuperUsuario
          ? respaldo
          : respaldo.filter((r) => r.nombre.toUpperCase() !== 'ADMINISTRADOR');
      },
    });
  }

  cargarUsuario(id: number): void {
    this.usuarioService.getUsuario(id).subscribe({
      next: (usuario) => {
        // Blindaje jerárquico: un admin estándar no puede editar administradores ni superadmins
        const esTargetAdmin =
          usuario.is_superuser ||
          (usuario.rol &&
            typeof usuario.rol === 'object' &&
            usuario.rol.nombre?.toUpperCase() === 'ADMINISTRADOR');

        const esPropio =
          id === this.authService.getUsuarioId() ||
          usuario.email === this.authService.getEmail();

        if (!this.esSuperUsuario && esTargetAdmin && !esPropio) {
          this.modalService.error('Acción reservada al Super Administrador.');
          this.router.navigate(['/dashboard/lista-usuarios']);
          return;
        }

        // Asegurar que el rol actual esté en la lista para que el select lo muestre correctamente
        if (usuario.rol && typeof usuario.rol === 'object' && usuario.rol.id) {
          const existe = this.roles.some((r) => r.id === usuario.rol.id);
          if (!existe) {
            this.roles = [...this.roles, usuario.rol];
          }
        }

        const rolId =
          usuario.rol && typeof usuario.rol === 'object'
            ? usuario.rol.id
            : usuario.rol;

        this.usuarioForm.patchValue({
          nombre: usuario.nombre,
          dni: usuario.dni,
          email: usuario.email,
          fecha_nacimiento: usuario.fecha_nacimiento,
          rol: rolId ? String(rolId) : '',
        });

        // Si es el usuario propio o no es Super Admin, bloquear alteracion de rol
        if (esPropio || (!this.esSuperUsuario && esTargetAdmin)) {
          this.usuarioForm.get('rol')?.disable();
        }
      },
      error: (err) => {
        console.error('Error al traer usuario', err);
        this.modalService.error('Error al cargar los datos del usuario.');
        this.router.navigate(['/dashboard/lista-usuarios']);
      },
    });
  }

  extraerError(err: any): string {
    if (!err?.error) return 'Error de comunicación con el servidor.';
    if (typeof err.error === 'string') return err.error;
    if (err.error.error) return err.error.error;
    if (err.error.detail) return err.error.detail;
    if (err.error.detalle) return err.error.detalle;
    if (err.error.mensaje) return err.error.mensaje;
    if (typeof err.error === 'object') {
      const keys = Object.keys(err.error);
      if (keys.length > 0) {
        const campo = keys[0];
        const val = err.error[campo];
        const detalle = Array.isArray(val) ? val[0] : String(val);
        return `${campo.toUpperCase()}: ${detalle}`;
      }
    }
    return 'Datos inválidos. Por favor, revisá los campos del formulario.';
  }

  guardarUsuario(): void {
    if (this.usuarioForm.invalid) {
      this.usuarioForm.markAllAsTouched();
      return;
    }

    this.cargando = true;
    this.errorFormulario = '';
    const formValues = this.usuarioForm.getRawValue();

    const datosParaEnviar: any = {
      nombre: formValues.nombre.trim(),
      dni: String(formValues.dni).trim(),
      email: formValues.email.trim(),
      fecha_nacimiento: formValues.fecha_nacimiento,
      rol_id: Number(formValues.rol),
    };

    if (!this.esEdicion) {
      datosParaEnviar.password = formValues.password;
    }

    if (this.esEdicion && this.usuarioId) {
      // Modo edición (PUT sin contraseña)
      this.usuarioService.actualizarUsuario(this.usuarioId, datosParaEnviar).subscribe({
        next: () => {
          this.cargando = false;
          this.modalService.exito('¡Usuario actualizado con éxito!');
          this.router.navigate(['/dashboard/lista-usuarios']);
        },
        error: (err) => {
          this.cargando = false;
          console.error('Error al actualizar usuario', err);
          this.errorFormulario = this.extraerError(err);
          this.modalService.error(this.errorFormulario);
        },
      });
    } else {
      // Modo creación (POST con contraseña OWASP)
      this.usuarioService.crearUsuario(datosParaEnviar).subscribe({
        next: () => {
          this.cargando = false;
          this.modalService.exito('¡Usuario creado con éxito!');
          this.router.navigate(['/dashboard/lista-usuarios']);
        },
        error: (err) => {
          this.cargando = false;
          console.error('Error al crear usuario', err);
          this.errorFormulario = this.extraerError(err);
          this.modalService.error(this.errorFormulario);
        },
      });
    }
  }
}