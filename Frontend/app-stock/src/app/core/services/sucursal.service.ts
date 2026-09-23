import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Sucursal } from '../models/sucursal.model';
import { StockSucursal } from '../models/stock-sucursal.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SucursalService {
  private apiUrl = `${environment.apiUrl}/inventario/sucursales/`;

  constructor(private http: HttpClient) { }

  getAll(search?: string): Observable<Sucursal[]> {
    let params = new HttpParams();
    if (search && search.trim()) {
      params = params.set('search', search.trim());
    }
    return this.http.get<Sucursal[]>(this.apiUrl, { params });
  }

  getById(id: number): Observable<Sucursal> {
    return this.http.get<Sucursal>(`${this.apiUrl}${id}/`);
  }

  create(sucursal: Partial<Sucursal>): Observable<Sucursal> {
    return this.http.post<Sucursal>(this.apiUrl, sucursal);
  }

  update(id: number, sucursal: Partial<Sucursal>): Observable<Sucursal> {
    return this.http.put<Sucursal>(`${this.apiUrl}${id}/`, sucursal);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  getInventario(id: number, search?: string, soloConStock?: boolean): Observable<StockSucursal[]> {
    let params = new HttpParams();
    if (search && search.trim()) {
      params = params.set('search', search.trim());
    }
    if (soloConStock) {
      params = params.set('solo_con_stock', 'true');
    }
    return this.http.get<StockSucursal[]>(`${this.apiUrl}${id}/inventario/`, { params });
  }
}