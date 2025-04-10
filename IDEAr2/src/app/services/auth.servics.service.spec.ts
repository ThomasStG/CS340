import { TestBed } from '@angular/core/testing';

import { AuthServicsService } from './auth.servics.service';

describe('AuthServicsService', () => {
  let service: AuthServicsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthServicsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
