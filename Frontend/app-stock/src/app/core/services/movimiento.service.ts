import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movimiento } from '../models/movimiento.model';
import { environment } from '../../../environments/environment';

export interface MovimientoFiltros {
  id_suc?: number;
  tipo?: string;
  id_art?: number;
}

@Injectable({ providedIn: 'root' })
export class MovimientoService {
  private apiUrl = `${environment.apiUrl}/inventario/movimientos/`;

  constructor(private http: HttpClient) { }

  getAll(filtros?: MovimientoFiltros): Observable<Movimiento[]> {
    let params = new HttpParams();
    if (filtros) {
      if (filtros.id_suc !== undefined && filtros.id_suc !== null) {
        params = params.set('id_suc', filtros.id_suc.toString());
      }
      if (filtros.tipo && filtros.tipo.trim()) {
        params = params.set('tipo', filtros.tipo.trim());
      }
      if (filtros.id_art !== undefined && filtros.id_art !== null) {
        params = params.set('id_art', filtros.id_art.toString());
      }
    }
    return this.http.get<Movimiento[]>(this.apiUrl, { params });
  }

  getById(id: number): Observable<Movimiento> {
    return this.http.get<Movimiento>(`${this.apiUrl}${id}/`);
  }

  create(movimiento: Movimiento): Observable<Movimiento> {
    return this.http.post<Movimiento>(this.apiUrl, movimiento);
  }

  update(id: number, movimiento: Movimiento): Observable<Movimiento> {
    return this.http.put<Movimiento>(`${this.apiUrl}${id}/`, movimiento);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}