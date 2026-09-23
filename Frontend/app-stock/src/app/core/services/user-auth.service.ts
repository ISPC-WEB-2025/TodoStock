import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserAuthService {
  private loginURL = `${environment.apiUrl}/usuarios/login/`;
  private registroURL = `${environment.apiUrl}/usuarios/registro/`;
  private refreshURL = `${environment.apiUrl}/usuarios/token/refresh/`;

  constructor(private http: HttpClient, private router: Router) { }

  login(email: string, password: string, recordar: boolean = false): Observable<any> {
    return this.http.post<any>(this.loginURL, { email, password }).pipe(
      tap(response => {
        const accessToken = response.access || response.token;
        if (accessToken) {
          // Limpiar ambos para evitar colisiones de sesiones previas
          localStorage.clear();
          sessionStorage.clear();

          const storage = recordar ? localStorage : sessionStorage;
          storage.setItem('nombre_usuario', response.nombre);
          storage.setItem('access_token', accessToken);
          storage.setItem('auth_token', accessToken); // Retrocompatibilidad
          if (response.refresh) {
            storage.setItem('refresh_token', response.refresh);
          }
          storage.setItem('es_admin', response.es_admin.toString());
          storage.setItem('es_empleado', response.es_empleado.toString());

          if (recordar) {
            localStorage.setItem('login_timestamp', Date.now().toString());
          }
        }
      })
    );
  }

  registrar(nombre: string, email: string, dni: number, fdn: any, password: string): Observable<any> {
    return this.http.post<any>(this.registroURL, {
      nombre, 
      email, 
      dni, 
      fdn, 
      password
    }).pipe(
      tap(response => {
        console.log('Usuario registrado con exito.', response);
      })
    );
  }

  getAccessToken(): string | null {
    return (
      localStorage.getItem('access_token') ||
      sessionStorage.getItem('access_token') ||
      localStorage.getItem('auth_token') ||
      sessionStorage.getItem('auth_token')
    );
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
  }

  setAccessToken(token: string): void {
    if (localStorage.getItem('refresh_token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token')) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('auth_token', token);
    } else {
      sessionStorage.setItem('access_token', token);
      sessionStorage.setItem('auth_token', token);
    }
  }

  refreshToken(): Observable<any> {
    const refresh = this.getRefreshToken();
    return this.http.post<any>(this.refreshURL, { refresh }).pipe(
      tap(response => {
        if (response && response.access) {
          this.setAccessToken(response.access);
        }
      })
    );
  }

  getToken(): string | null {
    return this.getAccessToken();
  }

  getUsername(): string | null {
    return localStorage.getItem('nombre_usuario') || sessionStorage.getItem('nombre_usuario');
  }

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    const loginTimestamp = localStorage.getItem('login_timestamp');
    if (loginTimestamp) {
      const now = Date.now();
      const expirationMs = 5 * 24 * 60 * 60 * 1000; // 5 días en milisegundos
      if (now - parseInt(loginTimestamp, 10) > expirationMs) {
        this.logout();
        return false;
      }
    }
    
    return true; 
  }

  isAdmin(): boolean {
    return (localStorage.getItem('es_admin') || sessionStorage.getItem('es_admin')) === 'true';
  }

  logout(): void {
    localStorage.clear(); // Borramos los datos de sesion y localStorage
    sessionStorage.clear();

    // Recargamos la pagina y redirigimos al login, tambien para evitar problemas a priori
    this.router.navigate(['/login']).then(() => {
      window.location.reload(); 
    });
  }
}
