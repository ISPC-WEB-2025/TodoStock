import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
} from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';

import { SucursalService } from '../../core/services/sucursal.service';
import { ModalService } from '../../core/services/modal.service';
import { Sucursal } from '../../core/models/sucursal.model';

@Component({
  selector: 'app-form-sucursal',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './form-sucursal.component.html',
  styleUrl: './form-sucursal.component.css',
})
export class FormSucursalComponent implements OnInit {
  sucursalForm!: FormGroup;
  esEdicion: boolean = false;
  idSucursal: number | null = null;
  cargando: boolean = false;
  guardando: boolean = false;
  erroresBackend: any = null;

  constructor(
    private fb: FormBuilder,
    private sucursalService: SucursalService,
    private modalService: ModalService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.detectarModoEdicion();
  }

  initForm(): void {
    this.sucursalForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.maxLength(100)]],
      direccion: ['', [Validators.required, Validators.maxLength(300)]],
      es_central: [false],
    });
  }

  detectarModoEdicion(): void {
    const idParam = this.route.snapshot.params['id'];
    if (idParam) {
      this.esEdicion = true;
      this.idSucursal = Number(idParam);
      this.cargarDatosSucursal(this.idSucursal);
    }
  }

  cargarDatosSucursal(id: number): void {
    this.cargando = true;
    this.sucursalService.getById(id).subscribe({
      next: (sucursal: Sucursal) => {
        this.sucursalForm.patchValue({
          nombre: sucursal.nombre,
          direccion: sucursal.direccion,
          es_central: sucursal.es_central ?? false,
        });
        this.cargando = false;
      },
      error: () => {
        this.modalService.error('No se pudo cargar la información de la sucursal solicitada.');
        this.cargando = false;
        this.router.navigate(['/dashboard/sucursales']);
      },
    });
  }

  guardar(): void {
    this.erroresBackend = null;

    if (this.sucursalForm.invalid) {
      this.sucursalForm.markAllAsTouched();
      return;
    }

    this.guardando = true;
    const datosSucursal: Partial<Sucursal> = {
      ...(this.idSucursal ? { id_suc: this.idSucursal } : {}),
      nombre: this.sucursalForm.value.nombre.trim(),
      direccion: this.sucursalForm.value.direccion.trim(),
    };

    if (this.esEdicion && this.idSucursal) {
      this.sucursalService.update(this.idSucursal, datosSucursal).subscribe({
        next: () => {
          this.guardando = false;
          this.modalService.exito('Sucursal actualizada exitosamente.');
          this.router.navigate(['/dashboard/sucursales']);
        },
        error: (err) => {
          this.guardando = false;
          this.manejarErrorBackend(err);
        },
      });
    } else {
      this.sucursalService.create(datosSucursal).subscribe({
        next: () => {
          this.guardando = false;
          this.modalService.exito('Sucursal creada exitosamente con auto-inicialización de stock.');
          this.router.navigate(['/dashboard/sucursales']);
        },
        error: (err) => {
          this.guardando = false;
          this.manejarErrorBackend(err);
        },
      });
    }
  }

  private manejarErrorBackend(err: any): void {
    if (err.error) {
      if (typeof err.error === 'object') {
        this.erroresBackend = err.error;
      } else {
        this.erroresBackend = { general: err.error };
      }
    } else {
      this.erroresBackend = {
        general: 'Error de comunicación con el servidor. Verificá que el backend esté en ejecución.',
      };
    }
  }

  cancelar(): void {
    this.router.navigate(['/dashboard/sucursales']);
  }
}
