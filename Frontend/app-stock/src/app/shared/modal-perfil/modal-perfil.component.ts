import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { UsuarioService } from '../../core/services/usuario.service';
import { UserAuthService } from '../../core/services/user-auth.service';
import { ModalService } from '../../core/services/modal.service';
import { Usuario } from '../../core/models/usuario.model';

@Component({
  selector: 'app-modal-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './modal-perfil.component.html',
  styleUrl: './modal-perfil.component.css'
})
export class ModalPerfilComponent implements OnInit, OnChanges {
  @Input() mostrar: boolean = false;
  @Output() cerrar = new EventEmitter<void>();

  private fb = inject(FormBuilder);
  private usuarioService = inject(UsuarioService);
  private authService = inject(UserAuthService);
  private modalService = inject(ModalService);

  cargando: boolean = false;
  guardandoPerfil: boolean = false;
  guardandoPassword: boolean = false;
  solicitandoBaja: boolean = false;
  confirmandoBaja: boolean = false;

  pestanaActiva: 'datos' | 'seguridad' | 'baja' = 'datos';
  perfil: Usuario | null = null;
  errorPerfil: string = '';
  errorPassword: string = '';
  verPasswordActual: boolean = false;
  verPasswordNueva: boolean = false;

  perfilForm: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2)]],
    dni: ['', [Validators.required, Validators.pattern('^[0-9]{7,8}$')]],
    fecha_nacimiento: ['', Validators.required]
  });

  passwordForm: FormGroup = this.fb.group({
    password_actual: ['', Validators.required],
    nueva_password: [
      '',
      [
        Validators.required,
        Validators.minLength(9),
        Validators.pattern(/^(?=.*[a-zA-Z])(?=.*\d)(?=.*[^a-zA-Z\d\s])\S+$/)
      ]
    ]
  });

  ngOnInit(): void {
    if (this.mostrar) {
      this.cargarDatos();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mostrar'] && this.mostrar) {
      this.cargarDatos();
    }
  }

  cargarDatos(): void {
    this.cargando = true;
    this.errorPerfil = '';
    this.errorPassword = '';
    this.confirmandoBaja = false;

    this.usuarioService.getMiPerfil().subscribe({
      next: (data) => {
        this.perfil = data;
        this.perfilForm.patchValue({
          nombre: data.nombre,
          dni: data.dni,
          fecha_nacimiento: data.fecha_nacimiento
        });
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar perfil:', err);
        this.errorPerfil = 'No se pudo cargar la información de tu perfil.';
        this.cargando = false;
      }
    });
  }

  guardarDatos(): void {
    if (this.perfilForm.invalid) {
      this.perfilForm.markAllAsTouched();
      return;
    }

    this.guardandoPerfil = true;
    this.errorPerfil = '';
    const formVals = this.perfilForm.value;

    this.usuarioService.actualizarMiPerfil({
      nombre: formVals.nombre.trim(),
      dni: String(formVals.dni).trim(),
      fecha_nacimiento: formVals.fecha_nacimiento
    }).subscribe({
      next: (actualizado) => {
        this.guardandoPerfil = false;
        this.modalService.exito('¡Perfil actualizado con éxito!');
        // Actualizar nombre en storage y vista
        if (actualizado.nombre) {
          const storage = localStorage.getItem('access_token') ? localStorage : sessionStorage;
          storage.setItem('nombre_usuario', actualizado.nombre);
        }
        this.cerrarModal();
        window.location.reload();
      },
      error: (err) => {
        this.guardandoPerfil = false;
        console.error('Error al actualizar perfil:', err);
        this.errorPerfil = err.error?.error || err.error?.detail || 'Error al guardar los cambios.';
      }
    });
  }

  cambiarPassword(): void {
    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.guardandoPassword = true;
    this.errorPassword = '';
    const formVals = this.passwordForm.value;

    this.usuarioService.cambiarMiPassword({
      password_actual: formVals.password_actual,
      nueva_password: formVals.nueva_password
    }).subscribe({
      next: (res) => {
        this.guardandoPassword = false;
        this.modalService.exito(res?.mensaje || '¡Contraseña actualizada exitosamente!');
        this.passwordForm.reset();
        this.cerrarModal();
      },
      error: (err) => {
        this.guardandoPassword = false;
        console.error('Error al cambiar contraseña:', err);
        this.errorPassword = err.error?.error || err.error?.detail || 'Error al cambiar la contraseña.';
      }
    });
  }

  confirmarDarmeDeBaja(): void {
    this.solicitandoBaja = true;
    this.usuarioService.darmeDeBaja().subscribe({
      next: (res) => {
        this.solicitandoBaja = false;
        this.modalService.exito(res?.mensaje || 'Tu cuenta ha sido desactivada.');
        this.cerrarModal();
        this.authService.logout();
      },
      error: (err) => {
        this.solicitandoBaja = false;
        console.error('Error al darse de baja:', err);
        const msg = err.error?.error || err.error?.detail || 'No fue posible desactivar la cuenta.';
        this.modalService.error(msg);
      }
    });
  }

  cerrarModal(): void {
    this.confirmandoBaja = false;
    this.errorPerfil = '';
    this.errorPassword = '';
    this.cerrar.emit();
  }
}
