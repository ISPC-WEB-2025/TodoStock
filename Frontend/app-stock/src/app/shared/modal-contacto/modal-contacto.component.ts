import { Component, Input, Output, EventEmitter, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UsuarioService } from '../../core/services/usuario.service';
import { UserAuthService } from '../../core/services/user-auth.service';
import { ModalService } from '../../core/services/modal.service';

@Component({
  selector: 'app-modal-contacto',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './modal-contacto.component.html',
  styleUrl: './modal-contacto.component.css'
})
export class ModalContactoComponent implements OnInit {
  @Input() mostrar: boolean = false;
  @Output() cerrar = new EventEmitter<void>();

  private fb = inject(FormBuilder);
  private usuarioService = inject(UsuarioService);
  private authService = inject(UserAuthService);
  private modalService = inject(ModalService);

  enviando: boolean = false;
  errorMensaje: string = '';

  contactoForm: FormGroup = this.fb.group({
    asunto: ['', [Validators.required, Validators.minLength(3)]],
    mensaje: ['', [Validators.required, Validators.minLength(5)]],
    email: ['', [Validators.required, Validators.email]]
  });

  ngOnInit(): void {
    const emailSesion = this.authService.getEmail();
    if (emailSesion) {
      this.contactoForm.patchValue({ email: emailSesion });
    }
  }

  enviar(): void {
    if (this.contactoForm.invalid) {
      this.contactoForm.markAllAsTouched();
      return;
    }

    this.enviando = true;
    this.errorMensaje = '';
    const formVals = this.contactoForm.value;

    this.usuarioService.enviarContacto({
      asunto: formVals.asunto.trim(),
      mensaje: formVals.mensaje.trim(),
      email: formVals.email ? formVals.email.trim() : undefined
    }).subscribe({
      next: (res) => {
        this.enviando = false;
        this.modalService.exito(res?.mensaje || '¡Consulta recibida con éxito!');
        this.contactoForm.reset();
        const emailSesion = this.authService.getEmail();
        if (emailSesion) {
          this.contactoForm.patchValue({ email: emailSesion });
        }
        this.cerrar.emit();
      },
      error: (err) => {
        this.enviando = false;
        console.error('Error al enviar consulta de contacto:', err);
        this.errorMensaje = err.error?.error || 'Hubo un error al enviar tu consulta. Intentá nuevamente.';
      }
    });
  }

  cerrarModal(): void {
    this.errorMensaje = '';
    this.cerrar.emit();
  }
}
