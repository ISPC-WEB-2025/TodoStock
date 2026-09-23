export interface Sucursal {
  id_suc: number;
  nombre: string;
  direccion: string;
  es_central?: boolean;
  total_articulos?: number;
  articulos_con_stock?: number;
  articulos_sin_stock?: number;
  articulos_alerta?: number;
}