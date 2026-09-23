import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http'; // ← agregás HttpParams
import { Observable } from 'rxjs';
import { Producto } from '../models/producto.model';
import { StockSucursal } from '../models/stock-sucursal.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProductoService {
  private apiUrl = `${environment.apiUrl}/inventario/productos/`;

  constructor(private http: HttpClient) { }

  getAll(): Observable<Producto[]> {
    return this.http.get<Producto[]>(this.apiUrl);
  }

  getById(id: number): Observable<Producto> {
    return this.http.get<Producto>(`${this.apiUrl}${id}/`);
  }

  buscarProductos(search: string): Observable<Producto[]> {
    if (!search || !search.trim()) {
      return this.http.get<Producto[]>(this.apiUrl);
    }
    const params = new HttpParams().set('search', search.trim());
    return this.http.get<Producto[]>(this.apiUrl, { params });
  }

  create(producto: Producto): Observable<Producto> {
    return this.http.post<Producto>(this.apiUrl, producto);
  }

  update(id: number, producto: Producto): Observable<Producto> {
    return this.http.put<Producto>(`${this.apiUrl}${id}/`, producto);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  getStockPorProducto(id: number): Observable<StockSucursal[]> {
    return this.http.get<StockSucursal[]>(`${this.apiUrl}${id}/stock/`);
  }
}
