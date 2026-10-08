import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Usuario } from '../../core/models/usuario.model';
import { UsuarioService } from '../../core/services/usuario.service';
import { UserAuthService } from '../../core/services/user-auth.service';
import { ModalService } from '../../core/services/modal.service';

@Component({
  selector: 'app-lista-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './lista-usuarios.component.html',
  styleUrl: './lista-usuarios.component.css'
})
export class ListaUsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  cargando: boolean = true;
  esSuperUsuario: boolean = false;

  // Estado del modal de desactivación
  mostrarModalDesactivar: boolean = false;
  usuarioADesactivar: Usuario | null = null;
  procesandoDesactivar: boolean = false;

  // Estado del modal de reseteo administrativo de contraseña (ADR-0008)
  mostrarModalReset: boolean = false;
  usuarioAResetear: Usuario | null = null;
  nuevaPassword: string = '';
  verPassword: boolean = false;
  procesandoReset: boolean = false;
  errorReset: string = '';

  private usuarioService = inject(UsuarioService);
  private authService = inject(UserAuthService);
  private modalService = inject(ModalService);

  ngOnInit(): void {
    this.esSuperUsuario = this.authService.isSuperUser();
    // Si la sesión proviene de antes de la actualización, sincronizamos con /api/usuarios/me/
    this.authService.obtenerPerfilActual().subscribe({
      next: () => {
        this.esSuperUsuario = this.authService.isSuperUser();
      },
      error: () => {
        // Mantener valor existente en caso de desconexión
      }
    });
    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.cargando = true;
    this.usuarioService.getUsuarios().subscribe({
      next: (data) => {
        this.usuarios = data;
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al traer los usuarios:', err);
        this.modalService.error('Error al cargar la lista de usuarios.');
        this.cargando = false;
      }
    });
  }

  // --- Jerarquía Administrativa y Autoservicio de Perfil (ADR-0008 / #US12) ---

  esUsuarioActual(usuario: Usuario): boolean {
    const miId = this.authService.getUsuarioId();
    if (miId && usuario.id === miId) return true;
    const miEmail = this.authService.getEmail();
    if (miEmail && usuario.email === miEmail) return true;
    return false;
  }

  esAdminTarget(usuario: Usuario): boolean {
    if (usuario.is_superuser) return true;
    if (!usuario.rol) return false;
    if (typeof usuario.rol === 'object' && usuario.rol.nombre) {
      return usuario.rol.nombre.toUpperCase() === 'ADMINISTRADOR';
    }
    return false;
  }

  puedeEditar(usuario: Usuario): boolean {
    if (this.esSuperUsuario) return true;
    if (this.esUsuarioActual(usuario)) return true; // El usuario siempre puede editar su propio perfil (US12)
    return !this.esAdminTarget(usuario);
  }

  puedeOperar(usuario: Usuario): boolean {
    if (this.esSuperUsuario) return true;
    return !this.esAdminTarget(usuario);
  }

  puedeDesactivar(usuario: Usuario): boolean {
    // Nadie puede desactivar al Super Administrador raíz ni auto-desactivarse en la grilla
    if (usuario.is_superuser) return false;
    if (this.esUsuarioActual(usuario)) return false;
    if (this.esSuperUsuario) return true;
    return !this.esAdminTarget(usuario);
  }

  puedeResetearClave(usuario: Usuario): boolean {
    if (this.esUsuarioActual(usuario)) return false; // Para la cuenta propia se debe usar Mi Perfil con clave actual
    if (this.esSuperUsuario) return true;
    return !this.esAdminTarget(usuario);
  }

  obtenerTooltip(usuario: Usuario): string {
    if (usuario.is_superuser) {
      return 'Cuenta de Super Administrador principal.';
    }
    if (this.esUsuarioActual(usuario)) {
      return 'Tu propia cuenta de usuario.';
    }
    if (!this.esSuperUsuario && this.esAdminTarget(usuario)) {
      return 'Acción reservada al Super Administrador.';
    }
    return '';
  }

  // --- Activación / Aprobación de Cuentas (#298 / #266) ---

  aprobarUsuario(usuario: Usuario): void {
    if (!usuario.id || !this.puedeOperar(usuario)) return;

    this.usuarioService.activarUsuario(usuario.id).subscribe({
      next: () => {
        const accion = !usuario.rol ? 'aprobada' : 'reactivada';
        this.modalService.exito(`¡Cuenta de ${usuario.nombre} ${accion} correctamente!`);
        this.cargarUsuarios();
      },
      error: (err) => {
        console.error('Error al activar usuario:', err);
        const msg = err.error?.detail || err.error?.error || 'Hubo un error al activar la cuenta.';
        this.modalService.error(msg);
      }
    });
  }

  // --- Modal de Desactivación (Soft-delete) ---

  abrirModalDesactivar(usuario: Usuario): void {
    if (!this.puedeDesactivar(usuario)) return;
    this.usuarioADesactivar = usuario;
    this.mostrarModalDesactivar = true;
  }

  cerrarModalDesactivar(): void {
    this.usuarioADesactivar = null;
    this.mostrarModalDesactivar = false;
    this.procesandoDesactivar = false;
  }

  confirmarDesactivacion(): void {
    if (!this.usuarioADesactivar?.id) return;

    this.procesandoDesactivar = true;
    this.usuarioService.eliminarUsuario(this.usuarioADesactivar.id).subscribe({
      next: () => {
        this.modalService.exito('Usuario desactivado correctamente.');
        this.cerrarModalDesactivar();
        this.cargarUsuarios();
      },
      error: (err) => {
        console.error('Error al desactivar usuario:', err);
        this.procesandoDesactivar = false;
        const msg = err.error?.detail || err.error?.error || 'Hubo un problema al desactivar el usuario.';
        this.modalService.error(msg);
      }
    });
  }

  // --- Modal de Reseteo Administrativo de Contraseña (ADR-0008) ---

  abrirModalReset(usuario: Usuario): void {
    if (!this.puedeOperar(usuario)) return;
    this.usuarioAResetear = usuario;
    this.nuevaPassword = '';
    this.errorReset = '';
    this.verPassword = false;
    this.procesandoReset = false;
    this.mostrarModalReset = true;
  }

  cerrarModalReset(): void {
    this.usuarioAResetear = null;
    this.nuevaPassword = '';
    this.errorReset = '';
    this.verPassword = false;
    this.procesandoReset = false;
    this.mostrarModalReset = false;
  }

  validarPasswordOWASP(p: string): string | null {
    if (!p || p.length < 9) {
      return 'La contraseña debe tener al menos 9 caracteres.';
    }
    if (/\s/.test(p)) {
      return 'La contraseña no puede contener espacios en blanco.';
    }
    if (!/[a-zA-Z]/.test(p)) {
      return 'La contraseña debe incluir al menos una letra.';
    }
    if (!/\d/.test(p)) {
      return 'La contraseña debe incluir al menos un número.';
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(p)) {
      return 'La contraseña debe incluir al menos un carácter especial (ej. !@#$%^&*).';
    }
    return null;
  }

  confirmarResetPassword(): void {
    if (!this.usuarioAResetear?.id) return;

    const errorValidacion = this.validarPasswordOWASP(this.nuevaPassword);
    if (errorValidacion) {
      this.errorReset = errorValidacion;
      return;
    }

    this.procesandoReset = true;
    this.errorReset = '';

    this.usuarioService.resetPassword(this.usuarioAResetear.id, this.nuevaPassword).subscribe({
      next: (res) => {
        const msg = res?.mensaje || `Contraseña de ${this.usuarioAResetear?.nombre} restablecida con éxito.`;
        this.modalService.exito(msg);
        this.cerrarModalReset();
      },
      error: (err) => {
        console.error('Error al resetear contraseña:', err);
        this.procesandoReset = false;
        this.errorReset = err.error?.error || err.error?.detail || 'Hubo un error al restablecer la contraseña.';
      }
    });
  }
}
