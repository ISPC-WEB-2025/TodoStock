import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProductoProveedor } from '../models/producto-proveedor.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProductoProveedorService {
  private apiUrl = `${environment.apiUrl}/producto-proveedor/`;

  constructor(private http: HttpClient) {}

  getAll(): Observable<ProductoProveedor[]> {
    return this.http.get<ProductoProveedor[]>(this.apiUrl);
  }

  getById(id: number): Observable<ProductoProveedor> {
    return this.http.get<ProductoProveedor>(`${this.apiUrl}${id}/`);
  }

  create(pp: ProductoProveedor): Observable<ProductoProveedor> {
    return this.http.post<ProductoProveedor>(this.apiUrl, pp);
  }

  update(id: number, pp: ProductoProveedor): Observable<ProductoProveedor> {
    return this.http.put<ProductoProveedor>(`${this.apiUrl}${id}/`, pp);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}