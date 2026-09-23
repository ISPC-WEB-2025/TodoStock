import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { throwError } from 'rxjs';
import { authInterceptor } from './auth.interceptor';
import { UserAuthService } from '../services/user-auth.service';

describe('authInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let authServiceSpy: jasmine.SpyObj<UserAuthService>;

  beforeEach(() => {
    authServiceSpy = jasmine.createSpyObj('UserAuthService', [
      'getAccessToken',
      'getRefreshToken',
      'refreshToken',
      'logout',
    ]);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: UserAuthService, useValue: authServiceSpy },
      ],
    });

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('debe adjuntar Bearer token en peticiones normales si existe token', () => {
    authServiceSpy.getAccessToken.and.returnValue('mock-access-token');

    httpClient.get('/api/inventario/productos/').subscribe();

    const req = httpMock.expectOne('/api/inventario/productos/');
    expect(req.request.headers.get('Authorization')).toBe('Bearer mock-access-token');
    req.flush([]);
  });

  it('NO debe adjuntar Bearer token en endpoints de autenticación (/login/, /registro/, /token/refresh/)', () => {
    authServiceSpy.getAccessToken.and.returnValue('mock-access-token');

    httpClient.post('/api/usuarios/login/', {}).subscribe();
    httpClient.post('/api/usuarios/registro/', {}).subscribe();
    httpClient.post('/api/usuarios/token/refresh/', {}).subscribe();

    const reqLogin = httpMock.expectOne('/api/usuarios/login/');
    const reqReg = httpMock.expectOne('/api/usuarios/registro/');
    const reqRef = httpMock.expectOne('/api/usuarios/token/refresh/');

    expect(reqLogin.request.headers.has('Authorization')).toBeFalse();
    expect(reqReg.request.headers.has('Authorization')).toBeFalse();
    expect(reqRef.request.headers.has('Authorization')).toBeFalse();

    reqLogin.flush({});
    reqReg.flush({});
    reqRef.flush({});
  });

  it('debe ejecutar logout() una única vez y cortar la cadena ante error 401 en /token/refresh/ (sin loop infinito)', () => {
    authServiceSpy.getAccessToken.and.returnValue('expired-access-token');
    authServiceSpy.getRefreshToken.and.returnValue('expired-refresh-token');

    // Retorna error 401 observable al invocar refreshToken
    authServiceSpy.refreshToken.and.returnValue(
      throwError(() => ({ status: 401, statusText: 'Unauthorized' }))
    );

    let errorReceived = false;
    httpClient.get('/api/inventario/productos/').subscribe({
      next: () => fail('La petición debió fallar con error 401'),
      error: (err) => {
        errorReceived = true;
      },
    });

    // Petición inicial falla con 401
    const reqInitial = httpMock.expectOne('/api/inventario/productos/');
    reqInitial.flush({ detail: 'Token expirado' }, { status: 401, statusText: 'Unauthorized' });

    // Se verifica que authService.logout() fue invocado exactamente una vez
    expect(authServiceSpy.logout).toHaveBeenCalledTimes(1);
    expect(errorReceived).toBeTrue();
  });
});
