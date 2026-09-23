import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { MovimientoService, MovimientoFiltros } from '../../../core/services/movimiento.service';
import { Movimiento } from '../../../core/models/movimiento.model';
import { SucursalService } from '../../../core/services/sucursal.service';
import { Sucursal } from '../../../core/models/sucursal.model';

@Component({
  selector: 'app-lista-movimientos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './lista-movimientos.component.html',
  styleUrl: './lista-movimientos.component.css',
})
export class ListaMovimientosComponent implements OnInit {
  movimientos: Movimiento[] = [];
  cargando = true;
  error = '';
  sucursales: Sucursal[] = [];
  sucursalSeleccionada: number | null = null;

  constructor(
    private movimientoService: MovimientoService,
    private sucursalService: SucursalService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.cargarMovimientos();
    this.cargarSucursales();
  }

  cargarMovimientos(): void {
    this.cargando = true;
    this.error = '';

    const filtros: MovimientoFiltros = {};
    if (this.sucursalSeleccionada !== null && this.sucursalSeleccionada !== undefined) {
      filtros.id_suc = this.sucursalSeleccionada;
    }

    this.movimientoService.getAll(filtros).subscribe({
      next: (data) => {
        this.movimientos = data;
        this.cargando = false;
      },
      error: () => {
        this.error = 'No se pudieron cargar los movimientos.';
        this.cargando = false;
      },
    });
  }

  cargarSucursales(): void {
    this.sucursalService.getAll().subscribe({
      next: (data) => {
        this.sucursales = data;
      },
      error: () => {
        console.error('Error al cargar la lista de sucursales para el filtro.');
      },
    });
  }

  onCambioSucursal(): void {
    this.cargarMovimientos();
  }

  irNuevoMovimiento(): void {
    if (this.router.url.startsWith('/dashboard')) {
      this.router.navigate(['/dashboard/movimientos/nuevo']);
    } else {
      this.router.navigate(['/vendedor/movimientos/nuevo']);
    }
  }

  esTrasladoIngreso(mov: Movimiento): boolean {
    return (
      mov.tipo === 'Traslado' &&
      !!mov.motivo &&
      (mov.motivo.startsWith('Recepción') || mov.motivo.includes('desde'))
    );
  }

  esTrasladoEgreso(mov: Movimiento): boolean {
    return (
      mov.tipo === 'Traslado' &&
      !!mov.motivo &&
      (mov.motivo.startsWith('Traslado hacia') || mov.motivo.includes('hacia'))
    );
  }
}
