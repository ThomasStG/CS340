import { TestBed } from '@angular/core/testing';

import { ElectricalUpdateService } from './electrical-update.service';

describe('ElectricalUpdateService', () => {
  let service: ElectricalUpdateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ElectricalUpdateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
