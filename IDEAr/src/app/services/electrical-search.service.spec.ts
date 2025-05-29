import { TestBed } from '@angular/core/testing';

import { ElectricalSearchService } from './electrical-search.service';

describe('ElectricalSearchService', () => {
  let service: ElectricalSearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ElectricalSearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
