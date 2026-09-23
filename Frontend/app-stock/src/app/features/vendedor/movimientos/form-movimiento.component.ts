import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

import { MovimientoService } from '../../../core/services/movimiento.service';
import { ProductoService } from '../../../core/services/producto.service';
import { StockSucursalService } from '../../../core/services/stock-sucursal.service';
import { ProveedorService } from '../../../core/services/proveedor.service';
import { SucursalService } from '../../../core/services/sucursal.service';
import { UserAuthService } from '../../../core/services/user-auth.service';
import { Producto } from '../../../core/models/producto.model';
import { StockSucursal } from '../../../core/models/stock-sucursal.model';
import { Proveedor } from '../../../core/models/proveedor.model';

@Component({
  selector: 'app-form-movimiento',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './form-movimiento.component.html',
  styleUrl: './form-movimiento.component.css',
})
export class FormMovimientoComponent implements OnInit {
  formulario: FormGroup;
  todosLosProductos: Producto[] = [];
  todoElStock: StockSucursal[] = [];
  sucursales: { id: number; nombre: string; es_central?: boolean }[] = [];
  sucursalesOrigen: { id: number; nombre: string; es_central?: boolean }[] = [];
  sucursalesDestino: { id: number; nombre: string }[] = [];
  todosLosProveedores: Proveedor[] = [];
  proveedoresFiltrados: Proveedor[] = [];
  tieneProveedoresAsociados = false;
  mostrarTodosLosProveedores = false;
  productosFiltrados: Producto[] = [];
  stockDisponible: number | null = null;
  guardando = false;
  errorMsg = '';
  exitoso = false;
  esAdmin = false;

  constructor(
    private fb: FormBuilder,
    private movimientoService: MovimientoService,
    private productoService: ProductoService,
    private stockService: StockSucursalService,
    private proveedorService: ProveedorService,
    private sucursalService: SucursalService,
    private userAuthService: UserAuthService,
    private router: Router
  ) {
    this.formulario = this.fb.group({
      tipo: ['', Validators.required],
      id_suc: ['', Validators.required],
      id_suc_destino: [''],
      id_art: ['', Validators.required],
      id_prov: [''],
      cantidad: ['', [Validators.required, Validators.min(1)]],
      motivo: ['', [Validators.maxLength(255)]],
    });
  }

  ngOnInit(): void {
    this.esAdmin = this.userAuthService.isAdmin();

    this.productoService.getAll().subscribe({
      next: (data) => (this.todosLosProductos = data),
      error: () => (this.errorMsg = 'No se pudieron cargar los productos.'),
    });

    this.sucursalService.getAll().subscribe({
      next: (data) => {
        this.sucursales = data.map((s) => ({
          id: s.id_suc,
          nombre: s.nombre,
          es_central: s.es_central,
        }));
        this.actualizarSucursalesOrigenPorTipo(this.formulario.get('tipo')?.value);
      },
      error: () => (this.errorMsg = 'No se pudieron cargar las sucursales.'),
    });

    this.stockService.getAll().subscribe({
      next: (data) => {
        this.todoElStock = data;
      },
      error: () => (this.errorMsg = 'No se pudo cargar el stock.'),
    });

    if (this.esAdmin) {
      this.proveedorService.getAll().subscribe({
        next: (data) => {
          this.todosLosProveedores = data;
          this.proveedoresFiltrados = [...data];
        },
        error: (err) => console.error('Error cargando proveedores:', err),
      });
    }

    // Al cambiar tipo de movimiento
    this.formulario.get('tipo')?.valueChanges.subscribe((tipo) => {
      this.actualizarValidacionesPorTipo(tipo);
      this.actualizarProductosDisponibles();
    });

    // Al cambiar la sucursal origen
    this.formulario.get('id_suc')?.valueChanges.subscribe((idSucursal) => {
      this.formulario.get('id_art')?.reset('');
      this.formulario.get('id_prov')?.reset('');
      this.stockDisponible = null;
      this.actualizarSucursalesDestino(idSucursal);
      this.actualizarProductosDisponibles();
    });

    // Al cambiar el producto seleccionado
    this.formulario.get('id_art')?.valueChanges.subscribe((idProducto) => {
      this.actualizarStockDisponible();
      this.actualizarProveedoresPorProducto(idProducto);
    });
  }

  private actualizarValidacionesPorTipo(tipo: string): void {
    const destinoControl = this.formulario.get('id_suc_destino');
    if (tipo === 'Traslado') {
      destinoControl?.setValidators([Validators.required]);
    } else {
      destinoControl?.clearValidators();
      destinoControl?.reset('');
    }
    destinoControl?.updateValueAndValidity();

    if (tipo !== 'Entrada') {
      this.formulario.get('id_prov')?.reset('');
    }

    this.actualizarSucursalesOrigenPorTipo(tipo);
  }

  private actualizarSucursalesOrigenPorTipo(tipo: string): void {
    if (tipo === 'Entrada') {
      this.sucursalesOrigen = this.sucursales.filter((s) => s.es_central);
      const central = this.sucursalesOrigen[0];
      if (central && this.formulario.get('id_suc')?.value !== central.id) {
        this.formulario.get('id_suc')?.setValue(central.id);
      }
    } else {
      this.sucursalesOrigen = [...this.sucursales];
    }
  }

  private actualizarSucursalesDestino(idOrigen: any): void {
    if (!idOrigen) {
      this.sucursalesDestino = [];
      return;
    }
    const origenNum = Number(idOrigen);
    this.sucursalesDestino = this.sucursales.filter((s) => s.id !== origenNum);
  }

  private actualizarProductosDisponibles(): void {
    const tipo = this.formulario.get('tipo')?.value;
    const idSucursal = this.formulario.get('id_suc')?.value;

    if (!idSucursal) {
      this.productosFiltrados = [];
      return;
    }

    if (tipo === 'Entrada') {
      // En una entrada se puede ingresar cualquier producto del catálogo
      this.productosFiltrados = [...this.todosLosProductos];
    } else {
      // Para Salida o Traslado, filtramos los que tengan existencias mayores a 0
      const idsProductos = this.todoElStock
        .filter((s) => s.id_suc == idSucursal && Number(s.cantidad_stock) > 0)
        .map((s) => s.id_art);
      this.productosFiltrados = this.todosLosProductos.filter(
        (p) => p.id_art !== undefined && idsProductos.includes(p.id_art)
      );
    }

    // Si el producto seleccionado previamente ya no está disponible, resetearlo
    const idArtActual = this.formulario.get('id_art')?.value;
    if (idArtActual && !this.productosFiltrados.some((p) => p.id_art == idArtActual)) {
      this.formulario.get('id_art')?.reset('');
      this.stockDisponible = null;
    }
  }

  private actualizarStockDisponible(): void {
    const idProducto = this.formulario.get('id_art')?.value;
    const idSucursal = this.formulario.get('id_suc')?.value;

    if (idProducto && idSucursal) {
      const registro = this.todoElStock.find(
        (s) => s.id_art == idProducto && s.id_suc == idSucursal
      );
      this.stockDisponible = registro ? registro.cantidad_stock : 0;
    } else {
      this.stockDisponible = null;
    }
  }

  private actualizarProveedoresPorProducto(idProducto: any): void {
    this.mostrarTodosLosProveedores = false;

    if (!idProducto) {
      this.tieneProveedoresAsociados = false;
      this.proveedoresFiltrados = [...this.todosLosProveedores];
      this.formulario.get('id_prov')?.reset('');
      return;
    }

    const prod = this.todosLosProductos.find((p) => p.id_art == idProducto);

    if (prod && prod.proveedores && prod.proveedores.length > 0) {
      this.tieneProveedoresAsociados = true;
      const idsHabituales = prod.proveedores.map((p) => p.id_prov);
      this.proveedoresFiltrados = this.todosLosProveedores.filter((p) =>
        idsHabituales.includes(p.id_prov)
      );

      // Si tiene exactamente 1 proveedor habitual registrado, lo pre-seleccionamos automáticamente
      if (this.proveedoresFiltrados.length === 1) {
        this.formulario.get('id_prov')?.setValue(this.proveedoresFiltrados[0].id_prov);
      } else {
        this.formulario.get('id_prov')?.reset('');
      }
    } else {
      this.tieneProveedoresAsociados = false;
      this.proveedoresFiltrados = [...this.todosLosProveedores];
      this.formulario.get('id_prov')?.reset('');
    }
  }

  toggleMostrarTodosProveedores(): void {
    this.mostrarTodosLosProveedores = !this.mostrarTodosLosProveedores;
    if (this.mostrarTodosLosProveedores) {
      this.proveedoresFiltrados = [...this.todosLosProveedores];
    } else {
      const idProducto = this.formulario.get('id_art')?.value;
      this.actualizarProveedoresPorProducto(idProducto);
    }
  }

  guardar(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    this.guardando = true;
    this.errorMsg = '';

    const formVal = this.formulario.value;
    const payload: any = {
      tipo: formVal.tipo,
      id_suc: Number(formVal.id_suc),
      id_art: Number(formVal.id_art),
      cantidad: Number(formVal.cantidad),
      motivo: formVal.motivo ? formVal.motivo.trim() : null,
      id_prov:
        formVal.tipo === 'Entrada' && formVal.id_prov
          ? Number(formVal.id_prov)
          : null,
      id_suc_destino:
        formVal.tipo === 'Traslado' && formVal.id_suc_destino
          ? Number(formVal.id_suc_destino)
          : null,
    };

    this.movimientoService.create(payload).subscribe({
      next: () => {
        this.exitoso = true;
        this.guardando = false;
        const returnUrl = this.router.url.startsWith('/dashboard')
          ? '/dashboard/movimientos'
          : '/vendedor/movimientos';
        setTimeout(() => this.router.navigate([returnUrl]), 1200);
      },
      error: (err) => {
        this.errorMsg =
          err.error?.error ||
          err.error?.detail ||
          'Error al registrar el movimiento.';
        if (err.error?.stock_disponible !== undefined) {
          this.errorMsg += ` Stock disponible: ${err.error.stock_disponible} unidades.`;
        }
        this.guardando = false;
      },
    });
  }

  cancelar(): void {
    const returnUrl = this.router.url.startsWith('/dashboard')
      ? '/dashboard/movimientos'
      : '/vendedor/movimientos';
    this.router.navigate([returnUrl]);
  }
}
