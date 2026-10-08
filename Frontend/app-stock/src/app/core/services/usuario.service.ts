import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Role, Usuario } from '../models/usuario.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/usuarios/`;

  // 1. GET: Traer la lista completa de usuarios
  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.apiUrl);
  }

  // 2. GET: Traer un solo usuario por su ID
  getUsuario(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}${id}/`);
  }

  // 3. POST: Crear un usuario nuevo
  crearUsuario(usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.post<Usuario>(this.apiUrl, usuario);
  }

  // 4. PUT: Actualizar un usuario existente
  actualizarUsuario(id: number, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}${id}/`, usuario);
  }

  // 5. PATCH: Activar o aprobar cuenta de usuario
  activarUsuario(id: number): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}${id}/`, { is_active: true });
  }

  // 6. PATCH: Cambiar estado de activación
  cambiarEstado(id: number, isActive: boolean): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}${id}/`, { is_active: isActive });
  }

  // 7. POST: Resetear contraseña administrativamente (ADR-0008)
  resetPassword(id: number, nuevaPassword: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}${id}/reset-password/`, { nueva_password: nuevaPassword });
  }

  // 8. GET: Listar roles disponibles del sistema
  getRoles(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.apiUrl}roles/`);
  }

  // 9. DELETE: Desactivar un usuario (soft delete en backend)
  eliminarUsuario(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${id}/`);
  }

  // --- Autoservicio de Perfil y Darme de Baja (US11 / US12 / ADR-0008) ---

  getMiPerfil(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}me/`);
  }

  actualizarMiPerfil(datos: { nombre?: string; dni?: string; fecha_nacimiento?: string }): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}me/`, datos);
  }

  cambiarMiPassword(datos: { password_actual: string; nueva_password: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}me/change-password/`, datos);
  }

  darmeDeBaja(): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}me/`);
  }

  // --- Contacto y Soporte (US04) ---

  enviarContacto(datos: { asunto: string; mensaje: string; email?: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}contacto/`, datos);
  }
}