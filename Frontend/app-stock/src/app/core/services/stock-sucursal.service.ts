import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { StockSucursal } from '../models/stock-sucursal.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class StockSucursalService {
  private apiUrl = `${environment.apiUrl}/inventario/stock/`;

  constructor(private http: HttpClient) { }

  getAll(): Observable<StockSucursal[]> {
    return this.http.get<StockSucursal[]>(this.apiUrl);
  }

  getById(id: number): Observable<StockSucursal> {
    return this.http.get<StockSucursal>(`${this.apiUrl}${id}/`);
  }

  create(stock: StockSucursal): Observable<StockSucursal> {
    return this.http.post<StockSucursal>(this.apiUrl, stock);
  }

  update(id: number, stock: Partial<StockSucursal>): Observable<StockSucursal> {
    return this.http.put<StockSucursal>(`${this.apiUrl}${id}/`, stock);
  }

  actualizarUmbral(id: number, stock_min: number): Observable<StockSucursal> {
    return this.http.patch<StockSucursal>(`${this.apiUrl}${id}/`, { stock_min });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}