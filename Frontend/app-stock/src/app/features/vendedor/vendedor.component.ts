import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { UserAuthService } from '../../core/services/user-auth.service';
import { ModalPerfilComponent } from '../../shared/modal-perfil/modal-perfil.component';
import { ModalContactoComponent } from '../../shared/modal-contacto/modal-contacto.component';

@Component({
  selector: 'app-vendedor',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet, ModalPerfilComponent, ModalContactoComponent],
  templateUrl: './vendedor.component.html',
  styleUrl: './vendedor.component.css'
})
export class VendedorComponent {
  private userAuthService: UserAuthService = inject(UserAuthService);
  protected readonly estaLogeado: boolean = this.userAuthService.isLoggedIn();
  protected readonly esAdmin: boolean = this.userAuthService.isAdmin();
  protected readonly nombreUsuario: string = this.userAuthService.getUsername() ?? '';

  mostrarModalPerfil: boolean = false;
  mostrarModalContacto: boolean = false;

  abrirPerfil(): void {
    this.mostrarModalPerfil = true;
  }

  cerrarPerfil(): void {
    this.mostrarModalPerfil = false;
  }

  abrirContacto(): void {
    this.mostrarModalContacto = true;
  }

  cerrarContacto(): void {
    this.mostrarModalContacto = false;
  }
}