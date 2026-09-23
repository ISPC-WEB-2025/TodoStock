import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { VendedorService } from '../../../core/services/vendedor.service';
import { StockSucursalService } from '../../../core/services/stock-sucursal.service';
import { StockSucursal } from '../../../core/models/stock-sucursal.model'

@Component({
  selector: 'app-catalogo',
  imports: [CommonModule, FormsModule],
  templateUrl: './catalogo.component.html',
  styleUrl: './catalogo.component.css'
})
export class CatalogoComponent implements OnInit {
  productos: any[] = [];
  stockTotal: StockSucursal[] = [];
  sucursales: { id: number, nombre: string }[] = [];
  sucursalSeleccionada: number | null = null;

  constructor(private vendedorService: VendedorService,
    private stockService: StockSucursalService) { }

  ngOnInit(): void {
    this.vendedorService.getProductos().subscribe(data => {
      this.productos = data;
    });

    // Cargar stock total para mostrar en el catálogo
    this.stockService.getAll().subscribe(data => {
      this.stockTotal = data;
      // Extraer sucursales únicas
      const mapa = new Map<number, string>();
      data.forEach(s => mapa.set(s.id_suc, s.nombre_sucursal ?? ''));
      this.sucursales = Array.from(mapa.entries()).map(([id, nombre]) => ({ id, nombre }));
    });
  }

  // Método para que solo muestre productos que tengan stock en la sucursal seleccionada
  get productosFiltrados(): any[] {
    if (!this.sucursalSeleccionada) return this.productos;
    return this.productos.filter(p =>
      this.stockTotal.some(
        s => s.id_art === p.id_art && s.id_suc === this.sucursalSeleccionada && Number(s.cantidad_stock) > 0
      )
    );
  }

  // Para mostrar el stock disponible en la sucursal seleccionada para cada producto
  getStockEnSucursal(idProducto: number): number | null {
    if (!this.sucursalSeleccionada) return null;
    const registro = this.stockTotal.find(
      s => s.id_art === idProducto && s.id_suc === this.sucursalSeleccionada
    );
    return registro ? registro.cantidad_stock : null;
  }
}

