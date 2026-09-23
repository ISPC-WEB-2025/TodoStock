import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';

import { ProductoService } from '../../core/services/producto.service';
import { CategoriaService } from '../../core/services/categoria.service';
import { SucursalService } from '../../core/services/sucursal.service';
import { StockSucursalService } from '../../core/services/stock-sucursal.service';
import { ModalService } from '../../core/services/modal.service';

import { Producto } from '../../core/models/producto.model';
import { Categoria } from '../../core/models/categoria.model';
import { Sucursal } from '../../core/models/sucursal.model';
import { StockSucursal } from '../../core/models/stock-sucursal.model';
import { ModalMermaComponent } from './modal-merma/modal-merma.component';

export interface ProductoConsolidado {
  id_art: number;
  nombre: string;
  codigo: string;
  categoriaNombre: string;
  id_cat: number | null;
  precio_venta: number;
  stock_min_global: number;
  stock_total: number;
  estado: 'optimo' | 'alerta' | 'sin-stock';
  sedes: StockSucursal[];
}

@Component({
  selector: 'app-stock-sucursal',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, ModalMermaComponent],
  templateUrl: './stock-sucursal.component.html',
  styleUrl: './stock-sucursal.component.css',
})
export class StockSucursalComponent implements OnInit {
  productosConsolidados: ProductoConsolidado[] = [];
  categorias: Categoria[] = [];
  sucursales: Sucursal[] = [];
  todosLosStocks: StockSucursal[] = [];

  cargando: boolean = true;
  error: string = '';

  // Filtros
  busqueda: string = '';
  categoriaFiltro: number | null = null;
  estadoFiltro: 'todos' | 'optimo' | 'alerta' | 'sin-stock' = 'todos';
  sucursalFiltro: number | null = null;

  // Acordeón de productos expandidos
  productosExpandidos: Set<number> = new Set<number>();

  // Estado para el Modal de Merma
  mostrarModalMerma: boolean = false;
  registroStockSeleccionado: StockSucursal | null = null;

  // Estado para el Modal Rápido de Umbral In-situ
  mostrarModalUmbral: boolean = false;
  registroUmbralSeleccionado: StockSucursal | null = null;
  nuevoUmbralValor: number = 0;
  guardandoUmbral: boolean = false;

  constructor(
    private productoService: ProductoService,
    private categoriaService: CategoriaService,
    private sucursalService: SucursalService,
    private stockService: StockSucursalService,
    private modalService: ModalService
  ) {}

  ngOnInit(): void {
    this.cargarDatosConsolidados();
  }

  cargarDatosConsolidados(): void {
    this.cargando = true;
    this.error = '';

    forkJoin({
      productos: this.productoService.getAll(),
      categorias: this.categoriaService.getAll(),
      sucursales: this.sucursalService.getAll(),
      stockList: this.stockService.getAll(),
    }).subscribe({
      next: ({ productos, categorias, sucursales, stockList }) => {
        this.categorias = categorias;
        this.sucursales = sucursales;
        this.todosLosStocks = stockList.map((s) => ({
          ...s,
          cantidad_stock: Number(s.cantidad_stock || 0),
          stock_min: Number(s.stock_min || 0),
        }));

        this.procesarConsolidado(productos, categorias, this.todosLosStocks);
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar datos de stock consolidado:', err);
        this.error = 'No se pudieron sincronizar los datos de stock con el backend.';
        this.cargando = false;
      },
    });
  }

  procesarConsolidado(
    productos: Producto[],
    categorias: Categoria[],
    stockList: StockSucursal[]
  ): void {
    const mapaCategorias = new Map<number, string>();
    categorias.forEach((c) => {
      if (c.id_cat !== undefined) {
        mapaCategorias.set(c.id_cat, c.nombre);
      }
    });

    this.productosConsolidados = productos.map((prod) => {
      const idArt = prod.id_art!;
      const sedesArt = stockList.filter((s) => s.id_art === idArt);

      const stockTotal = sedesArt.reduce((sum, s) => sum + s.cantidad_stock, 0);
      const stockMinGlobal = Number(prod.stock_min_global || 0);

      // Evaluar salud global del producto
      const tieneSedeAlerta = sedesArt.some(
        (s) => s.stock_min > 0 && s.cantidad_stock <= s.stock_min
      );

      let estado: 'optimo' | 'alerta' | 'sin-stock' = 'optimo';
      if (stockTotal === 0) {
        estado = 'sin-stock';
      } else if (
        (stockMinGlobal > 0 && stockTotal <= stockMinGlobal) ||
        tieneSedeAlerta
      ) {
        estado = 'alerta';
      }

      return {
        id_art: idArt,
        nombre: prod.nombre,
        codigo: prod.codigo,
        categoriaNombre: prod.id_cat ? (mapaCategorias.get(prod.id_cat) || 'Sin categoría') : 'Sin categoría',
        id_cat: prod.id_cat,
        precio_venta: Number(prod.precio_venta || 0),
        stock_min_global: stockMinGlobal,
        stock_total: stockTotal,
        estado,
        sedes: sedesArt,
      };
    });
  }

  // Filtrado reactivo en memoria
  get productosFiltrados(): ProductoConsolidado[] {
    return this.productosConsolidados.filter((item) => {
      // Filtro por texto (Nombre o Código)
      if (this.busqueda.trim()) {
        const query = this.busqueda.toLowerCase().trim();
        const coincideNombre = item.nombre.toLowerCase().includes(query);
        const coincideCodigo = item.codigo.toLowerCase().includes(query);
        if (!coincideNombre && !coincideCodigo) return false;
      }

      // Filtro por Categoría
      if (this.categoriaFiltro !== null) {
        if (item.id_cat !== this.categoriaFiltro) return false;
      }

      // Filtro por Estado
      if (this.estadoFiltro !== 'todos') {
        if (item.estado !== this.estadoFiltro) return false;
      }

      // Filtro por Sucursal
      if (this.sucursalFiltro !== null) {
        const sedeEncontrada = item.sedes.some(
          (s) => s.id_suc === this.sucursalFiltro && s.cantidad_stock > 0
        );
        if (!sedeEncontrada) return false;
      }

      return true;
    });
  }

  // Métricas Consolidadas
  get totalArticulos(): number {
    return this.productosConsolidados.length;
  }

  get totalUnidades(): number {
    return this.productosConsolidados.reduce((acc, p) => acc + p.stock_total, 0);
  }

  get articulosOptimos(): number {
    return this.productosConsolidados.filter((p) => p.estado === 'optimo').length;
  }

  get articulosAlerta(): number {
    return this.productosConsolidados.filter((p) => p.estado === 'alerta').length;
  }

  get articulosSinStock(): number {
    return this.productosConsolidados.filter((p) => p.estado === 'sin-stock').length;
  }

  // Métodos de Acordeón
  toggleExpandir(id_art: number): void {
    if (this.productosExpandidos.has(id_art)) {
      this.productosExpandidos.delete(id_art);
    } else {
      this.productosExpandidos.add(id_art);
    }
  }

  estaExpandido(id_art: number): boolean {
    return this.productosExpandidos.has(id_art);
  }

  expandirTodos(): void {
    this.productosFiltrados.forEach((p) => this.productosExpandidos.add(p.id_art));
  }

  colapsarTodos(): void {
    this.productosExpandidos.clear();
  }

  esSedeCentral(idSuc: number): boolean {
    return !!this.sucursales.find((s) => s.id_suc === idSuc)?.es_central;
  }

  // Modal Rápido de Umbral In-situ
  abrirModalUmbral(item: StockSucursal): void {
    this.registroUmbralSeleccionado = item;
    this.nuevoUmbralValor = item.stock_min;
    this.mostrarModalUmbral = true;
  }

  cerrarModalUmbral(): void {
    this.mostrarModalUmbral = false;
    this.registroUmbralSeleccionado = null;
    this.nuevoUmbralValor = 0;
  }

  ajustarPresetUmbral(delta: number): void {
    this.nuevoUmbralValor = Math.max(0, this.nuevoUmbralValor + delta);
  }

  guardarUmbral(): void {
    if (!this.registroUmbralSeleccionado) return;
    if (this.nuevoUmbralValor < 0) {
      this.modalService.error('El umbral mínimo no puede ser negativo.');
      return;
    }

    this.guardandoUmbral = true;
    const idStock = this.registroUmbralSeleccionado.id_stock;
    const nuevoMin = Number(this.nuevoUmbralValor);

    this.stockService.actualizarUmbral(idStock, nuevoMin).subscribe({
      next: (actualizado) => {
        // Actualizar localmente en memoria
        const reg = this.todosLosStocks.find((s) => s.id_stock === idStock);
        if (reg) {
          reg.stock_min = actualizado.stock_min;
        }

        // Recalcular estados
        this.productoService.getAll().subscribe((prods) => {
          this.procesarConsolidado(prods, this.categorias, this.todosLosStocks);
        });

        this.modalService.exito('Umbral de stock mínimo actualizado correctamente.');
        this.guardandoUmbral = false;
        this.cerrarModalUmbral();
      },
      error: () => {
        this.modalService.error('No se pudo actualizar el umbral de stock.');
        this.guardandoUmbral = false;
      },
    });
  }

  // Modal de Merma
  abrirModalMerma(item: StockSucursal): void {
    this.registroStockSeleccionado = item;
    this.mostrarModalMerma = true;
  }

  cerrarModalMerma(): void {
    this.mostrarModalMerma = false;
    this.registroStockSeleccionado = null;
  }

  onMermaCompletada(): void {
    this.cargarDatosConsolidados();
  }

  limpiarFiltros(): void {
    this.busqueda = '';
    this.categoriaFiltro = null;
    this.estadoFiltro = 'todos';
    this.sucursalFiltro = null;
  }
}
