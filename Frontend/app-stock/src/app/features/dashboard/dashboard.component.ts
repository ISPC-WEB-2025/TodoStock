import { Component, inject } from '@angular/core';
import { UserAuthService } from '../../core/services/user-auth.service';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { ModalPerfilComponent } from '../../shared/modal-perfil/modal-perfil.component';
import { ModalContactoComponent } from '../../shared/modal-contacto/modal-contacto.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, ModalPerfilComponent, ModalContactoComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
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
